package consumer

import slick.jdbc.PostgresProfile.api._
import scala.concurrent.{Await, Future}
import scala.concurrent.duration._
import scala.util.{Failure, Success, Try}
import scala.concurrent.ExecutionContext.Implicits.global

case class User(id: Option[Int] = None, name: String, age: Int)

class Users(tag: Tag) extends Table[User](tag, "users") {
  def id = column[Int]("id", O.PrimaryKey, O.AutoInc)
  def name = column[String]("name")
  def age = column[Int]("age")

  def * = (id.?, name, age) <> (User.tupled, User.unapply)
}

object Testdb {
  val users = TableQuery[Users]

  def main(args: Array[String]): Unit = {
    checkDatabase()
  }

  def checkDatabase(): Unit = {
    val db = Database.forURL(
      url = "jdbc:postgresql://db:5432/iot",
      user = "nafra",
      password = "test",
      driver = "org.postgresql.Driver"
    )

    val setup = DBIO.seq(users.schema.createIfNotExists)
    Await.result(db.run(setup), 5.seconds)
    println("Table created successfully!")

    val checkQuery: Future[Int] = db.run(sql"SELECT 1".as[Int].head)
    Try(Await.result(checkQuery, 2.seconds)) match {
      case Success(_) => println("db is up")
      case Failure(_) => println("db is not up")
    }
  }
}
