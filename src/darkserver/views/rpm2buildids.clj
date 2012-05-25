(ns darkserver.views.rpm2buildids
  (:require [darkserver.utils :as utils]
            [noir.response :as resp])
  (:use [darkserver.models.buildids]
        [noir.core :only [defpage]]))

(defpage [:get ["/rpm2buildids/:rpm"
                :rpm #"\p{Alnum}+-[\p{Alnum}.]+-[\p{Alnum}.]+"]]
  {:keys [rpm]}
  (resp/json
   (map (fn [result]
          {:buildid (result :buildid),
           :rpm (result :rpm),
           :elf (str (result :instpath) "/" (result :elfname)),
           :distro (result :distro)})
        (search-rpm (utils/strip-ending rpm ".rpm")))))
