# Set working directory automatically (works in VS Code terminal and RStudio)
get_script_path <- function() {
     args <- commandArgs(trailingOnly = FALSE)
     file_arg <- "--file="
     idx <- grep(file_arg, args)

     if (length(idx) > 0) {
          return(normalizePath(sub(file_arg, "", args[idx][1]), winslash = "/", mustWork = FALSE))
     }

     if (requireNamespace("rstudioapi", quietly = TRUE)) {
          p <- tryCatch(rstudioapi::getActiveDocumentContext()$path, error = function(e) "")
          if (nzchar(p)) {
               return(normalizePath(p, winslash = "/", mustWork = FALSE))
          }
     }

     return(normalizePath(getwd(), winslash = "/", mustWork = FALSE))
}

setwd(dirname(get_script_path()))

# Load dataset
data <- read.csv("../data/real_estate_data.csv")

print("Dataset:")
print(data)

# Summary
print("Summary:")
print(summary(data))

# Correlation
print("Correlation Matrix:")
print(cor(data))

# Scatter Plot
png("scatter_plot.png")
plot(data$Area, data$Price,
     main="Area vs Price",
     xlab="Area",
     ylab="Price",
     col="blue",
     pch=19)
dev.off()

# Regression Model
model <- lm(Price ~ Area + Bedrooms + Age + Distance_City + Location_Score, data=data)

print("Model Summary:")
print(summary(model))

# Prediction
new_house <- data.frame(
  Area=1400,
  Bedrooms=3,
  Age=5,
  Distance_City=3,
  Location_Score=9
)

pred <- predict(model, new_house)
print(paste("Predicted Price:", pred))

# Residual Plot
png("residual_plot.png")
plot(model$residuals,
     main="Residual Plot",
     col="red",
     pch=19)
abline(h=0)
dev.off()