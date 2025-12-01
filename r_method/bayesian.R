
data <- read.csv('../bonds_dashboards/fred_md.csv')
epu <- read.csv('../bonds_dashboards/epu_index.csv')
head(epu)
data$sasdate <- as.Date(data$sasdate, format = "%m/%d/%Y")
epu$DATE <- as.Date(epu$DATE)
epu$DATE <- epu$DATE + 1
data <- merge(data, epu, 
                       by.x = "sasdate", 
                       by.y = "DATE",
                       all = FALSE)# all=FALSE means inner join
auction <- read.csv('/Users/dylantoplas/Documents/ds4420/DS4420Project/bonds_dashboards/monthly_auction.csv')
head(auction)
auction$record_date <- as.Date(paste0(auction$record_date, "-01"), format = "%Y-%m-%d")
data <- merge(data, auction, 
              by.x = "sasdate", 
              by.y = "record_date",
              all = FALSE)# all=FALSE means inner join

nrow(data)
# ==============================================================================================================
library(brms)

# Fitting a normal model
# with some bells and whistles (lots of different options, see: https://cran.r-project.org/web/packages/brms/brms.pdf)
# For convenience, we'll use the default priors (you can check the docs for adjusting these as necessary)

features <- c('UNRATE', 'CPIAUCSL', 'INDPRO', 'PAYEMS', 'HOUST', 
              'USEPUINDXD', 'bid_to_cover_ratio_long', 'FEDFUNDS')

# Scale data
data_scaled <- data
data_scaled$GS10_lag <- c(0, head(data$GS10, -1))
data_scaled[, features] <- scale(data_scaled5[, features])  

# Build formula dynamically
formula_str <- paste("GS10 ~", paste(c(features, "GS10_lag"), collapse = " + "))
formula_obj <- as.formula(formula_str)

# Use the formula
prior <- default_prior(formula_obj, data = data_scaled, family = gaussian())

gs10_brm <- brm(formula_obj,
                family = gaussian(),
                data = data_scaled,
                chains = 4,
                cores = getOption("mc.cores", 1),
                iter = 4000,
                warmup = 720,
                thin = 2,
                prior = prior)

# Summary and diagnostics
# summary(gs10_brm)
# plot(gs10_brm)
bayes_R2(gs10_brm)

# Posterior predictions
post_preds <- posterior_predict(gs10_brm)
rate_post_preds <- post_preds[, nrow(data_scaled)]  
# hist(rate_post_preds)
# mean(rate_post_preds)

# Predict next observation - dynamically build new_data
last_obs <- tail(data_scaled, 1)
new_data <- as.data.frame(last_obs[, features])
new_data$GS10_lag <- last_obs$GS10

# Predict
future_pred <- posterior_predict(gs10_brm, newdata = new_data)

# GS1
data_scaled1 <- data
data_scaled1$GS1_lag <- c(0, head(data$GS1, -1))
data_scaled1[, features] <- scale(data_scaled1[, features]) 

# Build formula dynamically
formula_str <- paste("GS1 ~", paste(c(features, "GS1_lag"), collapse = " + "))
formula_obj <- as.formula(formula_str)

# Use the formula
prior1 <- default_prior(formula_obj, data = data_scaled1, family = gaussian())

gs1_brm <- brm(formula_obj,
                family = gaussian(),
                data = data_scaled51,
                chains = 4,
                cores = getOption("mc.cores", 1),
                iter = 4000,
                warmup = 720,
                thin = 2,
                prior = prior1)

# Summary and diagnostics
# summary(gs1_brm)
# plot(gs1_brm)
bayes_R2(gs1_brm)

# Posterior predictions
post_preds1 <- posterior_predict(gs1_brm)
rate_post_preds1 <- post_preds1[, nrow(data_scaled1)]  
# hist(rate_post_preds1)
# mean(rate_post_preds1)

# Predict next observation - dynamically build new_data
last_obs <- tail(data_scaled1, 1)
new_data <- as.data.frame(last_obs[, features])
new_data$GS1_lag <- last_obs$GS1

# Predict
future_pred1 <- posterior_predict(gs1_brm, newdata = new_data)
# hist(future_pred1, main = "Prediction for Next Month")
mean(future_pred1)  # Should be close to current rate (4.26%)
quantile(future_pred1, c(0.022, 0.972))  # 92% prediction interval



# GS5
data_scaled5 <- data
data_scaled5$GS5_lag <- c(0, head(data$GS5, -1))
data_scaled5[, features] <- scale(data_scaled5[, features]) 

# Build formula dynamically
formula_str <- paste("GS5 ~", paste(c(features, "GS5_lag"), collapse = " + "))
formula_obj <- as.formula(formula_str)

# Use the formula
prior <- default_prior(formula_obj, data = data_scaled5, family = gaussian())

gs5_brm <- brm(formula_obj,
                family = gaussian(),
                data = data_scaled5,
                chains = 4,
                cores = getOption("mc.cores", 1),
                iter = 4000,
                warmup = 720,
                thin = 2,
                prior = prior)

# Summary and diagnostics
# summary(gs5_brm)
# plot(gs5_brm)
bayes_R2(gs5_brm)

# Posterior predictions
post_preds5 <- posterior_predict(gs5_brm)
rate_post_preds5 <- post_preds5[, nrow(data_scaled5)]  
# hist(rate_post_preds5)
# mean(rate_post_preds5)

# Predict next observation - dynamically build new_data
last_obs5 <- tail(data_scaled5, 1)
new_data5 <- as.data.frame(last_obs5[, features])
new_data5$GS5_lag <- last_obs5$GS5

# Predict
future_pred5 <- posterior_predict(gs5_brm, newdata = new_data5)
# hist(future_pred5, main = "Prediction for Next Month")
mean(future_pred5)  # Should be close to current rate (4.56%)
quantile(future_pred5, c(0.055, 0.975))  # 95% prediction interval


# GS2 
g2 <- read.csv('/Users/dylantoplas/Documents/ds4420/DS4420Project/bonds_dashboards/GS2.csv')

head(g2)
names(g2)
# data <- read.csv('/Users/dylantoplas/Documents/ds4420/DS4420Project/bonds_dashboards/fred_md.csv')
# data <- data[-1, ]

# Check date formats
head(data$sasdate)
head(g2$observation_date)

# Convert dates to same format if needed
g2$observation_date <- as.Date(g2$observation_date)

# Inner join - keeps only matching dates
data_with_gs2 <- merge(data, g2, 
                       by.x = "sasdate", 
                       by.y = "observation_date",
                       all = FALSE)# all=FALSE means inner join



# Now scale and add lags
data_scaled2 <- data_with_gs2
data_scaled2$GS2_lag <- c(0, head(data_with_gs2$GS2, -1))
data_scaled2[, features] <- scale(data_scaled2[, features]) 

# Build formula dynamically
formula_str <- paste("GS2 ~", paste(c(features, "GS2_lag"), collapse = " + "))
formula_obj <- as.formula(formula_str)

# Use the formula
prior2 <- default_prior(formula_obj, data = data_scaled2, family = gaussian())

gs2_brm <- brm(formula_obj,
               family = gaussian(),
               data = data_scaled2,
               chains = 4,
               cores = getOption("mc.cores", 1),
               iter = 4000,
               warmup = 720,
               thin = 2,
               prior = prior2)

# Summary and diagnostics
# summary(gs2_brm)
# plot(gs2_brm)
bayes_R2(gs2_brm)

# Posterior predictions
post_preds2 <- posterior_predict(gs2_brm)
rate_post_preds2 <- post_preds2[, nrow(data_scaled2)]  
# hist(rate_post_preds2)
# mean(rate_post_preds2)

# Predict next observation - dynamically build new_data
last_obs2 <- tail(data_scaled2, 1)
new_data2 <- as.data.frame(last_obs2[, features])
new_data2$GS2_lag <- last_obs2$GS2

# Predict
future_pred2 <- posterior_predict(gs2_brm, newdata = new_data2)
# hist(future_pred2, main = "Prediction for Next Month")
mean(future_pred2)  # Should be close to current rate (4.26%)
quantile(future_pred2, c(0.022, 0.972))  # 92% prediction interval

yield_curve <- c(mean(rate_post_preds1),mean(rate_post_preds2),mean(rate_post_preds5),mean(rate_post_preds))
yield_curve
# 4.045306 3.735496 3.735496 3.897070