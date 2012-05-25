(ns darkserver.server
  (:require [noir.server :as server]
            [noir.statuses :as statuses])
  (:use darkserver.models
        [ring.util.response :only [resource-response]]))

(server/load-views "src/darkserver/views/")

(statuses/set-page! 404 (slurp (:body (resource-response "/public/404.html"))))
(statuses/set-page! 500 (slurp (:body (resource-response "/public/500.html"))))

(defn -main [& m]
  (let [mode (keyword (or (first m) :dev))
        port (Integer. (get (System/getenv) "PORT" "8080"))]
    ; TODO: find a way to initialize db pool properly here
    ; (initialize)
    (server/start port {:mode mode
                        :ns 'darkserver})))
