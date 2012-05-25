(ns darkserver.models.buildids
  (:use [darkserver.models]
        [korma.core]))

(initialize)
(defentity build-ids
  (table :buildid_gnubuildid)
  (entity-fields :build_id
                 :rpm_name
                 :elfname
                 :distro)
  (database db))

(defn search-buildid [id]
  (select build-ids
          (fields [:build_id :buildid]
                  [:rpm_name :rpm]
                  [:elfname :elf]
                  :distro)
          (where {:build_id id})))
