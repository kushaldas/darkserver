(ns darkserver.models
  (:require [darkserver.utils :as utils])
  (:use korma.db))

(declare db)

(defn read-config-into [cfg filename]
  (if (utils/file-exists? filename)
    (merge cfg
           (with-in-str (slurp filename)
             (read)))
    cfg))

(defn initialize
  "
Initializes the database connection.
This should really be done in server.clj only once,
but it seems that it's not then available to the individual entities
"
  []
  (when (not (bound? #'db))
    (let [cfg (-> {}
                  (read-config-into "/etc/darkserver/darkserverweb.conf")
                  (read-config-into (str (System/getProperty "user.home")
                                         "/.config/darkserverweb.conf")))]
      (assert (not (empty? cfg))
              "Missing configuration")
      (defdb db
        (mysql cfg)))))
