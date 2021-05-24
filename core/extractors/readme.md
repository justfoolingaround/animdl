# Extractors

Currently, there are only less than 10 sites supported; hence, this'll not be used for the time being.

In the near future when annoyingly a lot of sites are going to be supported, individual extractors will be removed and a extractor 
identifier based system will be placed. This, currently is a foundation for that system.

## Content Extraction Types

### Safe Extraction (Slow but accurate)

Extraction where the extractor behaves like a browser and makes AJAX/API requests to get the content the same way as the associated site does.

### Random Extraction (Fast but inaccurate)

Extraction where the URLs are searched through in the site itself and the whole process is based on luck factor and content availability factor.

### Curated-Random Extraction (Fast and accurate)

Extraction where the process may seem random but provides a guarenteed content yield.

<strong>
Note that Curated-Random Extraction algorithms are created by developers after they're certain that the algorithm is working perfectly in a standard use case. 
Curated random extraction is hence, an algorithm difficult to create, that is the main reason why this 'elite' algorithm group isn't all over the extractors. 
</strong>

## Usage (outside AnimDL)

These extractors provide single or multiple qualities availabile in the site. In an singular fetch, quality identification is difficult; 
hence, it is expected for the implementer to modify the returns as they require.