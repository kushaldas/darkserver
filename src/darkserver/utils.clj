(ns darkserver.utils
  (:import [java.io File]))

(defn file-exists? [filename]
  (let [f (File. filename)]
    (.exists f)))

(defn strip-ending [^String s,
                    ^String ending]
  (if (.endsWith s ending)
    (subs s 0 (- (.length s)
                 (.length ending)))
    s))
