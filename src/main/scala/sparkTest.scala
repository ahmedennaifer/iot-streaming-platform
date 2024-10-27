import org.apache.spark.sql.SparkSession
import org.apache.spark.streaming._
import org.apache.spark.streaming.StreamingContext._
import org.apache.spark.SparkContext
import org.apache.log4j.{Level, Logger}


object SparkConsummer {
  def main(args: Array[String]): Unit = {
    Logger.getLogger("org").setLevel(Level.ERROR)
    Logger.getLogger("akka").setLevel(Level.ERROR)
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

    val query = df.writeStream
      .outputMode("append")
      .format("console")
      .start()

    query.awaitTermination()
  }
}
