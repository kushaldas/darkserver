(ns darkserver.utils
  (:import [java.io File]))

(defn file-exists? [filename]
  (let [f (File. filename)]
    (.exists f)))
