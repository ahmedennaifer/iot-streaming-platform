import org.apache.spark.sql.SparkSession
import org.apache.spark.streaming._
import org.apache.spark.streaming.StreamingContext._
import org.apache.spark.SparkContext
import org.apache.log4j.{Level, Logger}
import org.apache.spark.sql.types.StructType
import org.apache.spark.sql.types.StructField
import org.apache.spark.sql.types._
import org.apache.spark.sql.functions._


object SparkConsummer {


  def main(args: Array[String]): Unit = {

    val floatTuple : (Option[Float], Option[Float]) = (Some(1.5f), None)

    val spark = SparkSession.builder
      .appName("ScalaConsummer")
      .master("local[2]")
      .getOrCreate

    val df = spark.readStream
      .format("kafka")
      .option("kafka.bootstrap.servers", "kafka:9092")
      .option("subscribe", "test")
      .option("includeHeaders", "true")
      .load()

    val schema = StructType(Array(
      StructField("DeviceId", StringType, nullable= false),
      StructField("DeviceModel", StringType, nullable=  true),
      StructField("Status", StringType, nullable= false),
      StructField("CurrentReading", FloatType, nullable= false),
      StructField("BatteryLevel", FloatType, nullable= false),
      StructField("Location", FloatType, nullable= false)
    ))

   
    val parsedDf = df
      .withColumn("jsonString", col("value").cast("string")) 
      .withColumn("data", from_json(col("jsonString"), schema))
      .select("data.*") 



    val query = parsedDf.writeStream
      .outputMode("append")
      .format("console")
      .start()

    query.awaitTermination()
  }
}
