import org.apache.spark.sql.SparkSession
import org.apache.spark.streaming._
import org.apache.spark.streaming.StreamingContext._
import org.apache.spark.SparkContext

object SparkConsummer {
  def main(args: Array[String]): Unit = {

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
