(ns darkserver.views.serverversion
  (:require [darkserver.properties :as props]
            [noir.response :as resp])
  (:use [noir.core :only [defpage]]))

(defpage "/serverversion" []
  (resp/json {:server-version props/version}))
