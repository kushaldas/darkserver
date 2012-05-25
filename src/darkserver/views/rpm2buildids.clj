(ns darkserver.views.rpm2buildids
  (:require [noir.response :as resp])
  (:use [darkserver.models.buildids]
        [noir.core :only [defpage]]))

(defpage [:get ["/rpm2buildids/:id" :id #".*"]] {:keys [id]}
  (resp/json
   (map (fn [result]
          {:buildid (result :buildid),
           :rpm (result :rpm),
           :elf (str (result :instpath) "/" (result :elfname)),
           :distro (result :distro)})
        (search-rpm id))))
