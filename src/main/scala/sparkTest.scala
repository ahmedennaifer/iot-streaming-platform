import org.apache.spark.sql.{SparkSession, DataFrame}

object SimpleDataFrameApp {
  def main(args: Array[String]): Unit = {
    val spark = SparkSession.builder()
      .appName("Simple DataFrame App")
      .master("local[*]") 
      .getOrCreate()


    val data = Seq(
      ("Alice", 28, "Software Engineer"),
      ("Bob", 34, "Data Scientist"),
      ("Charlie", 23, "Analyst")
    )

    val df: DataFrame = spark.createDataFrame(data).toDF("Name", "Age", "Job")

    df.show()

    spark.stop()
  }
}
