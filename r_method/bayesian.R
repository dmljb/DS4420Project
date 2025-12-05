library(brms)
# ======================================================
# Getting data
setwd("C:/Users/denis/DS4420Project/r_method")
data <- read.csv('fred_md.csv')
epu <- read.csv('epu_index.csv')
auction <- read.csv('monthly_auction.csv')
g2 <- read.csv('GS2.csv')

data$sasdate <- as.Date(data$sasdate, format = "%m/%d/%Y")
epu$DATE <- as.Date(epu$DATE) + 1
auction$record_date <- as.Date(paste0(auction$record_date, "-01"), format = "%Y-%m-%d")
g2$observation_date <- as.Date(g2$observation_date)

data <- merge(data, epu, by.x = "sasdate", by.y = "DATE", all = FALSE)
data <- merge(data, auction, by.x = "sasdate", by.y = "record_date", all = FALSE)
data_with_gs2 <- merge(data, g2, by.x = "sasdate", by.y = "observation_date", all = FALSE)

# ======================================================

fit_bayesian_model <- function(data, target_var, features, 
                               chains = 4, iter = 1000*4, warmup = 180*4, thin = 2,
                               cores = 4, verbose = FALSE) {
  
  lag_var <- paste0(target_var, "_lag")
  data[[lag_var]] <- c(0, head(data[[target_var]], -1))
  
  data[, features] <- scale(data[, features])
  
  formula_str <- paste(target_var, "~", paste(c(features, lag_var), collapse = " + "))
  formula_obj <- as.formula(formula_str)
  
  prior <- default_prior(formula_obj, data = data, family = gaussian())
  
  model <- brm(formula_obj,
               family = gaussian(),
               data = data,
               chains = chains,
               cores = cores,
               iter = iter,
               warmup = warmup,
               thin = thin,
               prior = prior,
               )
  
  return(list(model = model, data_scaled = data, features = features, target_var = target_var))
}

# ====================================================

test_bayesian_model <- function(result, test_size = 12) {
  model <- result$model
  data_scaled <- result$data_scaled
  target_var <- result$target_var
  features <- result$features
  
  # Split data
  train_data <- head(data_scaled, nrow(data_scaled) - test_size)
  test_data <- tail(data_scaled, test_size)
  
  # Predict on test set
  test_predictions <- predict(model, newdata = test_data, probs = c(0.025, 0.975))
  
  # Calculate metrics
  actual <- test_data[[target_var]]
  predicted <- test_predictions[, "Estimate"]
  lower_95 <- test_predictions[, "Q2.5"]
  upper_95 <- test_predictions[, "Q97.5"]
  
  rmse <- sqrt(mean((actual - predicted)^2))
  mae <- mean(abs(actual - predicted))
  
  cat("Testing for", target_var, "\n")
  cat("RMSE:                 ", round(rmse, 4), "\n")
  cat("MAE:                  ", round(mae, 4), "\n")

    return(list(actual = actual,
                predicted = predicted,
                lower_95 = lower_95,
                upper_95 = upper_95,
                rmse = rmse,
                mae = mae,
                target_var = target_var))
  
}
  
plot_test_results <- function(test_result) {
  test_size <- length(test_result$actual)
  
  plot(1:test_size, test_result$actual, type = "b", pch = 19, 
       ylim = range(c(test_result$actual, test_result$lower_95, test_result$upper_95)),
       xlab = "Month", ylab = test_result$target_var,
       main = paste(test_result$target_var, "- Out-of-Sample Test"))
  lines(1:test_size, test_result$predicted, col = "red", type = "b", pch = 17)
  
  polygon(c(1:test_size, rev(1:test_size)), 
          c(test_result$lower_95, rev(test_result$upper_95)),
          col = rgb(1, 0, 0, 0.2), border = NA)
  
  legend("bottomleft", c("Actual", "Predicted"), 
         col = c("black", "red", rgb(1, 0, 0)), 
         lty = c(1, 1, 1), pch = c(19, 17),
         cex = 0.5)
}

macro_features <- c('UNRATE', 'CPIAUCSL', 'INDPRO', 'PAYEMS', 'HOUST', 'USEPUINDXD')

auction_features <- c('bid_to_cover_ratio_', 'direct_bidder_tendered_', 
                      'indirect_bidder_tendered_', 'primary_dealer_tendered_',
                      'comp_tendered_', 'direct_bidder_accepted_', 
                      'indirect_bidder_accepted_', 'primary_dealer_accepted_', 
                      'comp_accepted_')

auction_features_long <- paste0(auction_features, "long")
auction_features_bills <- paste0(auction_features, "bills")
auction_features_medium <- paste0(auction_features, "medium")
auction_features_short <- paste0(auction_features, "short")

features_gs10 <- c(macro_features, 
                   auction_features_long, 'FEDFUNDS')

features_gs1 <- c(macro_features, 
                  auction_features_bills, 'FEDFUNDS')

features_gs5 <- c(macro_features, 
                  auction_features_medium, 'FEDFUNDS')

features_gs2 <- c(macro_features, 
                  auction_features_short, 'FEDFUNDS')

result_gs10 <- fit_bayesian_model(data, "GS10", features_gs10)
result_gs1 <- fit_bayesian_model(data, "GS1", features_gs1)
result_gs5 <- fit_bayesian_model(data, "GS5", features_gs5)
result_gs2 <- fit_bayesian_model(data_with_gs2, "GS2", features_gs2)

test_gs10 <- test_bayesian_model(result_gs10)
test_gs1 <- test_bayesian_model(result_gs1)
test_gs5 <- test_bayesian_model(result_gs5)
test_gs2 <- test_bayesian_model(result_gs2)

# For poster
par(mfrow = c(2, 2))
plot_test_results(test_gs10)
plot_test_results(test_gs1)
plot_test_results(test_gs5)
plot_test_results(test_gs2)


comparison <- data.frame(
  Model = c("GS1", "GS2", "GS5", "GS10"),
  RMSE = c(test_gs1$rmse, test_gs2$rmse, test_gs5$rmse, test_gs10$rmse),
  MAE = c(test_gs1$mae, test_gs2$mae, test_gs5$mae, test_gs10$mae),
)

print(comparison)

best_model_rmse <- comparison$Model[which.min(comparison$RMSE)]
cat("\nBest model by RMSE:", best_model_rmse, "\n")

best_model_mae <- comparison$Model[which.min(comparison$MAE)]
cat("\nBest model by MAE:", best_model_mae, "\n")


predict_next <- function(result) {
  last_obs <- tail(result$data_scaled, 1)
  lag_var <- paste0(result$target_var, "_lag")
  new_data <- last_obs[, c(result$features, lag_var)]
  pred <- posterior_predict(result$model, newdata = new_data)
  return(mean(pred))
}

future_gs1 <- predict_next(result_gs1)
future_gs2 <- predict_next(result_gs2)
future_gs5 <- predict_next(result_gs5)
future_gs10 <- predict_next(result_gs10)

yield_curve <- c(future_gs1, future_gs2, future_gs5, future_gs10)
yield_curve
# 4.089233 3.766546 3.407099 3.824731

bayes_preds <- data.frame(
  GS1 = test_gs1$predicted,
  GS2 = test_gs2$predicted,
  GS5 = test_gs5$predicted,
  GS10 = test_gs10$predicted
)

actual_yields <- data.frame(
  GS1 = test_gs1$actual,
  GS2 = test_gs2$actual,
  GS5 = test_gs5$actual,
  GS10 = test_gs10$actual
)

write.csv(bayes_preds, "bayesian_predictions.csv", row.names = FALSE)
write.csv(actual_yields, "actual_yields.csv", row.names = FALSE)
