import org.apache.spark.sql.SparkSession
import org.apache.spark.sql.types._
import org.apache.spark.sql.functions._

object SparkConsumer {

  def main(args: Array[String]): Unit = {

    val spark = SparkSession.builder
      .appName("ScalaConsumer")
      .master("local[2]")
      .getOrCreate()

    val schema = StructType(Array(
      StructField("DeviceId", StringType, nullable = false),
      StructField("DeviceModel", StringType, nullable = true),
      StructField("Status", StringType, nullable = false),
      StructField("CurrentReading", FloatType, nullable = false),
      StructField("BatteryLevel", FloatType, nullable = false),
      StructField("Location", FloatType, nullable = false)
    ))

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


    val query = parsedDf.writeStream
      .outputMode("append")
      .format("console")
      .option("truncate", "false")
      .start()

    query.awaitTermination()
  }
}
