(ns darkserver.views.index
  (:require [noir.response :as resp])
  (:use [noir.core :only [defpage]]))

(defpage "/" []
  (resp/redirect "/index.html"))
