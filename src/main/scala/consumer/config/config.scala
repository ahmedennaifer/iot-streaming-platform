package consumer.config

import io.github.cdimascio.dotenv.Dotenv

object Config {
  private val dotenv = Dotenv.load()

  object DatabaseConfig {
    val url = dotenv.get("DB_URL")
    val user = dotenv.get("DB_USER")
    val password = dotenv.get("DB_PASSWORD")
    val driver = dotenv.get("DB_DRIVER")
  }
}
