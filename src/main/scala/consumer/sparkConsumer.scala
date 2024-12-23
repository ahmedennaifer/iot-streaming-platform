package consumer

import org.apache.spark.sql.{SparkSession, DataFrame}
import org.apache.spark.sql.types._
import org.apache.spark.sql.functions._
import org.apache.spark.sql.streaming.Trigger

/*

  TODO: High priority : Window transformations max, mean, etc.. , Metada enrichment with joins, top N devices etc..
  TODO: Add grafana monitoring, eg: if temperature exceeds threshold, alert
  TODO: Add anomaly detection and alerting in real time
  TODO: add better simulation for sensors
  TODO: alert when sensor low battery
 */

object SparkConsumer {

  def main(args: Array[String]): Unit = {

    val spark = SparkSession.builder
      .appName("ScalaConsumer")
      .master("local[2]")
      .getOrCreate()

    import spark.implicits._

    val schema = StructType(
      Array(
        StructField("DeviceId", StringType, nullable = false),
        StructField("DeviceModel", StringType, nullable = true),
        StructField("DeviceType", StringType, nullable = false),
        StructField("Status", StringType, nullable = false),
        StructField("CurrentReading", FloatType, nullable = false),
        StructField("BatteryLevel", FloatType, nullable = false),
        StructField("Location", FloatType, nullable = false),
        StructField("Timestamp", TimestampType, nullable = false)
      )
    )

    val df = spark.readStream
      .format("kafka")
      .option("kafka.bootstrap.servers", "kafka:9092")
      .option("subscribe", "temperature, humidity")
      .option("includeHeaders", "true")
      .load()

    val parsedDf = df
      .selectExpr("CAST(value AS STRING) as json")
      .select(from_json(col("json"), schema).as("data"))
      .select("data.*")

    def writeToDatabase(batchDf: DataFrame, batchId: Long): Unit = {

      batchDf.show(truncate = false)

      batchDf.write
        .format("jdbc")
        .option("url", "jdbc:postgresql://db:5432/iot")
        .option("dbtable", "data")
        .option("user", "nafra")
        .option("password", "test")
        .option("driver", "org.postgresql.Driver")
        .mode("append")
        .save()
    }

    val query = parsedDf.writeStream
      .foreachBatch(writeToDatabase _)
      .trigger(Trigger.ProcessingTime("2 seconds"))
      // .option("checkPointLocation", ".checkpoint/"s
      .outputMode("append")
      .start()

    query.awaitTermination()
  }
}
