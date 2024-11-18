package consumer

import org.apache.spark.sql.{SparkSession, DataFrame}
import org.apache.spark.sql.types._
import org.apache.spark.sql.functions._

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
        StructField("Status", StringType, nullable = false),
        StructField("CurrentReading", FloatType, nullable = false),
        StructField("BatteryLevel", FloatType, nullable = false),
        StructField("Location", FloatType, nullable = false)
      )
    )

    val df = spark.readStream
      .format("kafka")
      .option("kafka.bootstrap.servers", "kafka:9092")
      .option("subscribe", "test")
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
        .option("url", "jdbc:postgresql://db:5435/iot")
        .option("dbtable", "data")
        .option("user", "nafra")
        .option("password", "test")
        .option("driver", "org.postgresql.Driver")
        .mode("append")
        .save()
    }

    val query = parsedDf.writeStream
      .foreachBatch(writeToDatabase _)
      .outputMode("append")
      .start()

    query.awaitTermination()
  }
}
