Predict
=======

I noticed a lot of chess players who prepare themselves for the Belgian Interteam Competition.
They download the results of previous rounds, create a table and look up the games of the possible opponents.

This script does the hard work, by downloading the results, parsing the html pages, and preparing the tables.


Usage:
------

>$ python predict_nic.py -c 230 -r 5 -s 2 -t 1

The output will be something like this:

```
Leuven 1:
	code	NAME                           (elo ) ( s / g) avg  tpr 
	---1-	AKESSON RALF                   (2462) (0.0/ 1) 2365 1445
	-11-1	PEEK MAURICE                   (2375) (2.5/ 3) 2285 2565
	--22-	LEUNIS GEERT                   (2292) (1.5/ 2) 2244 2435
	-2332	TONOLI BENJAMIN                (2227) (1.0/ 4) 2264 2073
	--4-3	PRAET MAARTEN                  (2215) (1.0/ 2) 2168 2168
	-3--4	CEULEMANS KARL                 (2158) (0.0/ 2) 2230 1190
	--545	GOOSSENS ROEL                  (2155) (1.0/ 3) 2156 2035
	-4656	VERHEYDEN JONAS                (2148) (2.0/ 4) 2119 2119
	-5767	VAN ESPEN EDDY                 (2087) (1.5/ 4) 2104 2016
	-6-7-	VAN HUL CHRISTIAAN             (2062) (0.5/ 2) 2170 1980
	-7888	DELANOEIJE PATRICK             (2003) (1.5/ 4) 2008 1919
	-8---	DELAERE KOEN                   (1844) (1.0/ 3) 2098 1977
```

Warning:
--------
It's not idiot proof, also it cannot handle bad inputs very gratiously.

have fun,

Romain.


PS. Steff Helsen sent me a patch to include the ratings
