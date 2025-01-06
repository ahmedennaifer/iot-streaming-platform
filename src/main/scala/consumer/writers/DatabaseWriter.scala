package consumer.writers

import org.apache.spark.sql.DataFrame
import consumer.config.SparkConfig.DatabaseConfig._

object DatabaseWriter {
  def writeToDatabase(
      df: DataFrame,
      tableName: String,
      mode: String = "append"
  ): Unit = {
    df.write
      .format("jdbc")
      .option("url", url)
      .option("dbtable", tableName)
      .option("user", user)
      .option("password", password)
      .option("driver", driver)
      .mode(mode)
      .save()
  }

  object DataFrameTransformations {
    def prepareWindowedMetrics(df: DataFrame): DataFrame = {
      df.selectExpr(
        "window.start as window_start",
        "window.end as window_end",
        "DeviceType",
        "avg_reading",
        "max_reading",
        "min_reading",
        "stddev_reading",
        "avg_battery",
        "number_of_readings"
      )
    }

    def prepareDeviceHealth(df: DataFrame): DataFrame = {
      df.selectExpr(
        "window.start as window_start",
        "window.end as window_end",
        "DeviceType",
        "avg_battery",
        "error_count",
        "low_battery_count"
      )
    }

    def prepareAlertMetrics(df: DataFrame): DataFrame = {
      df.selectExpr(
        "window.start as window_start",
        "window.end as window_end",
        "DeviceType",
        "high_temp_alerts",
        "critical_battery_alerts",
        "error_alerts"
      )
    }
  }
}
