package consumer

import org.apache.spark.sql.functions._
import org.apache.spark.sql.streaming.Trigger
import org.apache.spark.sql.{DataFrame, Dataset, Row}
import consumer.config.SparkConfig
import consumer.processors.MetricsProcessor
import consumer.writers.DatabaseWriter
import consumer.writers.DatabaseWriter.DataFrameTransformations._

object SparkConsumer {
  def main(args: Array[String]): Unit = {
    val spark = SparkConfig.createSparkSession()

    val df = spark.readStream
      .format("kafka")
      .option("kafka.bootstrap.servers", SparkConfig.KafkaConfig.bootstrapServers)
      .option("subscribe", SparkConfig.KafkaConfig.topics)
      .option("includeHeaders", "true")
      .load()

    val parsedDf = df
      .selectExpr("CAST(value AS STRING) as json")
      .select(from_json(col("json"), SparkConfig.schema).as("data"))
      .select("data.*")

    val windowedMetrics = MetricsProcessor.calculateWindowedMetrics(parsedDf)
    val deviceHealth = MetricsProcessor.calculateDeviceHealth(parsedDf)
    val alertMetrics = MetricsProcessor.calculateAlertMetrics(parsedDf)

    val queries = Seq(
      parsedDf.writeStream
        .foreachBatch { (batchDf: Dataset[Row], _: Long) => 
          DatabaseWriter.writeToDatabase(batchDf, "data")
        }
        .trigger(Trigger.ProcessingTime("2 seconds"))
        .outputMode("append")
        .start(),

      // windowed_metrics
      windowedMetrics.writeStream
        .foreachBatch { (batchDf: Dataset[Row], _: Long) => 
          DatabaseWriter.writeToDatabase(
            prepareWindowedMetrics(batchDf),
            "windowed_metrics"
          )
        }
        .trigger(Trigger.ProcessingTime("1 minute"))
        .outputMode("update")
        .start(),

      // device_health
      deviceHealth.writeStream
        .foreachBatch { (batchDf: Dataset[Row], _: Long) => 
          DatabaseWriter.writeToDatabase(
            prepareDeviceHealth(batchDf),
            "device_health"
          )
        }
        .trigger(Trigger.ProcessingTime("1 minute"))
        .outputMode("update")
        .start(),

      // Alerts
      alertMetrics.writeStream
        .foreachBatch { (batchDf: Dataset[Row], _: Long) => 
          DatabaseWriter.writeToDatabase(
            prepareAlertMetrics(batchDf),
            "alert_metrics"
          )
        }
        .trigger(Trigger.ProcessingTime("1 minute"))
        .outputMode("update")
        .start()
    )

    spark.streams.awaitAnyTermination()
  }
}
