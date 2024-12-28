package consumer.processors

import org.apache.spark.sql.DataFrame
import org.apache.spark.sql.functions._
import consumer.config.SparkConfig.WindowConfig._

object MetricsProcessor {
  def calculateWindowedMetrics(parsedDf: DataFrame): DataFrame = {
    parsedDf
      .withWatermark("Timestamp", watermark)
      .groupBy(
        window(col("Timestamp"), windowDuration, slideDuration),
        col("DeviceType")
      )
      .agg(
        avg("CurrentReading").as("avg_reading"),
        max("CurrentReading").as("max_reading"),
        min("CurrentReading").as("min_reading"),
        stddev("CurrentReading").as("stddev_reading"),
        avg("BatteryLevel").as("avg_battery"),
        count("*").as("number_of_readings")
      )
  }

  def calculateDeviceHealth(parsedDf: DataFrame): DataFrame = {
    parsedDf
      .withWatermark("Timestamp", watermark)
      .groupBy(
        window(col("Timestamp"), windowDuration, slideDuration),
        col("DeviceType")
      )
      .agg(
        avg("BatteryLevel").as("avg_battery"),
        count(when(col("Status") === "ERROR", 1)).as("error_count"),
        count(when(col("BatteryLevel") < 20, 1)).as("low_battery_count")
      )
  }

  def calculateAlertMetrics(parsedDf: DataFrame): DataFrame = {
    parsedDf
      .withWatermark("Timestamp", watermark)
      .groupBy(
        window(col("Timestamp"), windowDuration, slideDuration),
        col("DeviceType")
      )
      .agg(
        count(when(col("CurrentReading") > 30, 1)).as("high_temp_alerts"),
        count(when(col("BatteryLevel") < 15, 1)).as("critical_battery_alerts"),
        count(when(col("Status") === "ERROR", 1)).as("error_alerts")
      )
  }
}
