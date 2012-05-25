(ns darkserver.views.buildids
  (:require [noir.response :as resp])
  (:use [darkserver.models.buildids]
        [noir.core :only [defpage]]))

(defpage [:get ["/buildids/:id" :id #".*"]] {:keys [id]}
  (resp/json (search-buildid id)))
