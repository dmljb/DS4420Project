
# Let's bring in some real data
data <- read.csv('bonds_dashboards/fred_md.csv')
tail(data$GS10)

library(brms)

# Fitting a normal model
# with some bells and whistles (lots of different options, see: https://cran.r-project.org/web/packages/brms/brms.pdf)
# For convenience, we'll use the default priors (you can check the docs for adjusting these as necessary)
data_scaled <- data
data_scaled$GS10_lag <- c(0, head(data$GS10, -1))
# data_scaled <- na.omit(data_scaled)
data_scaled[, c('UNRATE', 'CPIAUCSL', 'INDPRO', 'PAYEMS', 'HOUST')] <- scale(data_scaled[,c('UNRATE', 'CPIAUCSL', 'INDPRO', 'PAYEMS', 'HOUST')])
# data_scaled$GS10 <- as.factor(data_scaled$GS10) # llm categorical?
head(data_scaled)

prior <- default_prior(GS10 ~ UNRATE + CPIAUCSL + INDPRO + PAYEMS + HOUST + GS10_lag,
                       data = data_scaled,
                       family = gaussian())

gs10_brm <- brm(GS10 ~ UNRATE + CPIAUCSL + INDPRO + PAYEMS + HOUST + GS10_lag, # omit the special stats
                family = gaussian(), # data likelihood is normal
                data = data_scaled,
                chains = 4, # we should usually run more than a single chain
                cores = getOption("mc.cores", 1), # you can run those multiple chains in parallel if you want/can!
                iter =1000*4, # longer is probably better, but don't want to destroy my machine....
                warmup = 180*4, # the burn-in amount (default is 50%)
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
  HOUST = last_obs$HOUST
)

# Predict NEXT month
future_pred <- posterior_predict(gs10_brm, newdata = new_data)
hist(future_pred, main = "Prediction for Next Month")
mean(future_pred)  # Should be close to current rate (4.26%)
quantile(future_pred, c(0.025, 0.975))  # 95% prediction interval

