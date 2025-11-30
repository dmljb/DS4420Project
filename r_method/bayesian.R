
# Let's bring in some real data
data <- read.csv('bonds_dashboards/fred_md.csv')
library(brms)

# Fitting a normal model
# with some bells and whistles (lots of different options, see: https://cran.r-project.org/web/packages/brms/brms.pdf)
# For convenience, we'll use the default priors (you can check the docs for adjusting these as necessary)
data_scaled <- data
data_scaled$GS10_lag <- c(0, head(data$GS10, -1))
data_scaled[, c('UNRATE', 'CPIAUCSL', 'INDPRO', 'PAYEMS', 'HOUST')] <- scale(data_scaled[,c('UNRATE', 'CPIAUCSL', 'INDPRO', 'PAYEMS', 'HOUST')])
# data_scaled$GS10 <- as.factor(data_scaled$GS10) # llm categorical?
head(data_scaled)

prior <- default_prior(GS10 ~ UNRATE + CPIAUCSL + INDPRO + PAYEMS + HOUST + GS10_lag + FEDFUNDS,
                       data = data_scaled,
                       family = gaussian())

gs10_brm <- brm(GS10 ~ UNRATE + CPIAUCSL + INDPRO + PAYEMS + HOUST + GS10_lag + FEDFUNDS, # omit the special stats
                family = gaussian(), # data likelihood is normal
                data = data_scaled,
                chains = 4, # we should usually run more than a single chain
                cores = getOption("mc.cores", 1), # you can run those multiple chains in parallel if you want/can!
                iter =1000*4, # longer is probably better, but don't want to destroy my machine....
                warmup = 180*4, # the burn-in amount (default is 20%)
                thin = 2, # take every two (should probably only adjust this after a trial run to see if it's needed; default is 1)
                prior = prior)
# as with any MCMC sampling, especially with multiple chains and some thinning, this may take a minute or two...
# BUT; setting it up was pretty easy!

# Get overall summary
summary(gs10_brm)

# plot the posterior distributions/chains to assess convergence
plot(gs10_brm)

# there is even a Bayesian equivalent of R^2
bayes_R2(gs10_brm)

# posterior predictive distribution
post_preds <- posterior_predict(gs10_brm)
head(post_preds) # each row is a sample, each column a pokemon
# for last obv
bulb_post_preds <- post_preds[,801]
hist(bulb_post_preds)
mean(bulb_post_preds)



# predicting next observation
last_obs <- tail(data_scaled, 1)

new_data <- data.frame(
  GS10_lag = last_obs$GS10,
  UNRATE = last_obs$UNRATE,
  CPIAUCSL = last_obs$CPIAUCSL,
  INDPRO = last_obs$INDPRO,
  PAYEMS = last_obs$PAYEMS,
  HOUST = last_obs$HOUST,
  FEDFUNDS = last_obs$FEDFUNDS
)

# Predict NEXT month
future_pred <- posterior_predict(gs10_brm, newdata = new_data)
hist(future_pred, main = "Prediction for Next Month")
mean(future_pred)  # Should be close to current rate (4.26%)
quantile(future_pred, c(0.022, 0.972))  # 92% prediction interval




# GS1
data_scaled1 <- data
data_scaled1$GS1_lag <- c(0, head(data$GS1, -1))
data_scaled1[, c('UNRATE', 'CPIAUCSL', 'INDPRO', 'PAYEMS', 'HOUST')] <- scale(data_scaled1[,c('UNRATE', 'CPIAUCSL', 'INDPRO', 'PAYEMS', 'HOUST')])
# data_scaled1$GS10 <- as.factor(data_scaled1$GS10) # llm categorical?
head(data_scaled1)

prior <- default_prior(GS1 ~ UNRATE + CPIAUCSL + INDPRO + PAYEMS + HOUST + GS1_lag + FEDFUNDS,
                       data = data_scaled1,
                       family = gaussian())

gs1_brm <- brm(GS1 ~ UNRATE + CPIAUCSL + INDPRO + PAYEMS + HOUST + GS1_lag + FEDFUNDS, # omit the special stats
                family = gaussian(), # data likelihood is normal
                data = data_scaled1,
                chains = 4, # we should usually run more than a single chain
                cores = getOption("mc.cores", 1), # you can run those multiple chains in parallel if you want/can!
                iter =1000*4, # longer is probably better, but don't want to destroy my machine....
                warmup = 180*4, # the burn-in amount (default is 20%)
                thin = 2, # take every two (should probably only adjust this after a trial run to see if it's needed; default is 1)
                prior = prior)
# as with any MCMC sampling, especially with multiple chains and some thinning, this may take a minute or two...
# BUT; setting it up was pretty easy!

# Get overall summary
summary(gs1_brm)

# plot the posterior distributions/chains to assess convergence
plot(gs1_brm)

# there is even a Bayesian equivalent of R^2
bayes_R2(gs1_brm)

# posterior predictive distribution
post_preds1 <- posterior_predict(gs1_brm)
head(post_preds1) # each row is a sample, each column a pokemon
# for last obv
bulb_post_preds1 <- post_preds[,801]
hist(bulb_post_preds1)
mean(bulb_post_preds1)



# predicting next observation
last_obs1 <- tail(data_scaled1, 1)

new_data1 <- data.frame(
  GS1_lag = last_obs$GS1,
  UNRATE = last_obs$UNRATE,
  CPIAUCSL = last_obs$CPIAUCSL,
  INDPRO = last_obs$INDPRO,
  PAYEMS = last_obs$PAYEMS,
  HOUST = last_obs$HOUST,
  FEDFUNDS = last_obs$FEDFUNDS
)

# Predict NEXT month
future_pred1 <- posterior_predict(gs1_brm, newdata = new_data1)
hist(future_pred1, main = "Prediction for Next Month")
mean(future_pred1)  # Should be close to current rate (4.26%)
quantile(future_pred1, c(0.022, 0.972))  # 92% prediction interval



# GS5

data_scaled5 <- data
data_scaled5$GS5_lag <- c(0, head(data$GS5, -1))
data_scaled5[, c('UNRATE', 'CPIAUCSL', 'INDPRO', 'PAYEMS', 'HOUST')] <- scale(data_scaled5[,c('UNRATE', 'CPIAUCSL', 'INDPRO', 'PAYEMS', 'HOUST')])
# data_scaled5$GS5 <- as.factor(data_scaled5$GS5) # llm categorical?
head(data_scaled5)

prior <- default_prior(GS5 ~ UNRATE + CPIAUCSL + INDPRO + PAYEMS + HOUST + GS5_lag + FEDFUNDS,
                       data = data_scaled5,
                       family = gaussian())

gs5_brm <- brm(GS5 ~ UNRATE + CPIAUCSL + INDPRO + PAYEMS + HOUST + GS5_lag + FEDFUNDS, # omit the special stats
                family = gaussian(), # data likelihood is normal
                data = data_scaled5,
                chains = 4, # we should usually run more than a single chain
                cores = getOption("mc.cores", 1), # you can run those multiple chains in parallel if you want/can!
                iter =500*4, # longer is probably better, but don't want to destroy my machine....
                warmup = 180*4, # the burn-in amount (default is 50%)
                thin = 5, # take every two (should probably only adjust this after a trial run to see if it's needed; default is 1)
                prior = prior)
# as with any MCMC sampling, especially with multiple chains and some thinning, this may take a minute or two...
# BUT; setting it up was pretty easy!

# Get overall summary
summary(gs5_brm)

# plot the posterior distributions/chains to assess convergence
plot(gs5_brm)

# there is even a Bayesian equivalent of R^5
bayes_R2(gs5_brm)

# posterior predictive distribution
post_preds5 <- posterior_predict(gs5_brm)
head(post_preds5) # each row is a sample, each column a pokemon
# for last obv
bulb_post_preds5 <- post_preds[,801]
hist(bulb_post_preds5)
mean(bulb_post_preds5)



# predicting next observation
last_obs5 <- tail(data_scaled5, 1)

new_data5 <- data.frame(
  GS5_lag = last_obs5$GS5,
  UNRATE = last_obs5$UNRATE,
  CPIAUCSL = last_obs5$CPIAUCSL,
  INDPRO = last_obs5$INDPRO,
  PAYEMS = last_obs5$PAYEMS,
  HOUST = last_obs5$HOUST,
  FEDFUNDS = last_obs5$FEDFUNDS
)

# Predict NEXT month
future_pred5 <- posterior_predict(gs5_brm, newdata = new_data5)
hist(future_pred5, main = "Prediction for Next Month")
mean(future_pred5)  # Should be close to current rate (4.56%)
quantile(future_pred5, c(0.055, 0.975))  # 95% prediction interval


# GS2 
g2 <- read.csv('bonds_dashboards/GS2.csv')

head(g2)
names(g2)
data <- read.csv('bonds_dashboards/fred_md.csv')
data <- data[-1, ]

# Check date formats
head(data$sasdate)
head(g2$observation_date)

# Convert dates to same format if needed
data$sasdate <- as.Date(data$sasdate, format = "%m/%d/%Y")
g2$observation_date <- as.Date(g2$observation_date)

# Inner join - keeps only matching dates
data_with_gs2 <- merge(data, g2, 
                       by.x = "sasdate", 
                       by.y = "observation_date",
                       all = FALSE)# all=FALSE means inner join

# Check how many rows you kept
nrow(data)         # Original
nrow(g2)          # GS2 data
nrow(data_with_gs2) # After merge

range(g2$observation_date)
range(data$sasdate)

# Check date range
range(data_with_gs2$sasdate)

# Now scale and add lags
data_scaled2 <- data_with_gs2
data_scaled2$GS2_lag <- c(0, head(data_with_gs2$GS2, -1))

# Scale predictors
data_scaled2[, c('UNRATE', 'CPIAUCSL', 'INDPRO', 'PAYEMS', 'HOUST')] <- 
  scale(data_scaled2[, c('UNRATE', 'CPIAUCSL', 'INDPRO', 'PAYEMS', 'HOUST')])

# Remove first row (has NA for lags)
data_scaled2 <- data_scaled2[-1, ]

# Now fit GS2 model
gs2_brm <- brm(
  GS2 ~ UNRATE + CPIAUCSL + INDPRO + PAYEMS + HOUST + FEDFUNDS + GS2_lag,
  family = gaussian(),
  data = data_scaled2,
  chains = 4,
  cores = 4,
  iter = 4000,
  warmup = 720
)

summary(gs2_brm)

post_preds2 <- posterior_predict(gs2_brm)
head(post_preds2) # each row is a sample, each column a pokemon
# for last obv
bulb_post_preds2 <- post_preds[,593]
hist(bulb_post_preds2)
mean(bulb_post_preds2)

last_obs2 <- tail(data_scaled2, 1)
new_data2 <- data.frame(
  GS2_lag = last_obs2$GS2,
  UNRATE = last_obs2$UNRATE,
  CPIAUCSL = last_obs2$CPIAUCSL,
  INDPRO = last_obs2$INDPRO,
  PAYEMS = last_obs2$PAYEMS,
  HOUST = last_obs2$HOUST,
  FEDFUNDS = last_obs2$FEDFUNDS
)

future_pred2 <- posterior_predict(gs2_brm, newdata = new_data2)
hist(future_pred2, main = "Prediction for Next Month")
mean(future_pred2)  # Should be close to current rate (4.26%)
quantile(future_pred2, c(0.022, 0.972))  # 92% prediction interval

yield_curve <- c(mean(bulb_post_preds1),mean(bulb_post_preds2),mean(bulb_post_preds5),mean(bulb_post_preds))
# 4.43124 3.48048 4.43124 4.43124