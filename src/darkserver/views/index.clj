(ns darkserver.views.index
  (:use [noir.core :only [defpage]]
        [ring.util.response :only [resource-response]]))

(defpage "/" []
  (slurp (:body (resource-response "/public/index.html"))))
