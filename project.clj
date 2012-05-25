(defproject darkserver "0.5.90-SNAPSHOT"
  :description "GNU build-id web service"
  :url "https://github.com/kushaldas/darkserver"
  :license {:name "GPLv2+"
            :url "http://www.gnu.org/licenses/gpl-2.0.html"}
  :dependencies [[org.clojure/clojure "1.3.0"]
                 [korma "0.3.0-beta7"]
                 [mysql/mysql-connector-java "5.1.20"]
                 [noir "1.2.1"]]
  :plugins [[lein-immutant "0.7.2"]
            [lein-noir "1.2.1"]
            [lein-swank "1.4.4"]]
  :main darkserver.server)
