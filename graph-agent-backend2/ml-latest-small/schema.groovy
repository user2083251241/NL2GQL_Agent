// MovieLens 图模型 Schema (HugeGraph)
// 适用于 ml-latest-small 数据集 (有表头版本)

// ---------- 属性键 ----------
schema.propertyKey("userId").asInt().ifNotExist().create();
schema.propertyKey("movieId").asInt().ifNotExist().create();
schema.propertyKey("title").asText().ifNotExist().create();
schema.propertyKey("imdbId").asText().ifNotExist().create();
schema.propertyKey("tmdbId").asText().ifNotExist().create();
schema.propertyKey("name").asText().ifNotExist().create();
schema.propertyKey("rating").asFloat().ifNotExist().create();
schema.propertyKey("timestamp").asLong().ifNotExist().create();
schema.propertyKey("tag").asText().ifNotExist().create();

// ---------- 顶点标签 ----------
schema.vertexLabel("User")
    .properties("userId")
    .primaryKeys("userId")
    .ifNotExist().create();

schema.vertexLabel("Movie")
    .properties("movieId", "title", "imdbId", "tmdbId")
    .primaryKeys("movieId")
    .ifNotExist().create();

schema.vertexLabel("Genre")
    .properties("name")
    .primaryKeys("name")
    .ifNotExist().create();

// ---------- 边标签 ----------
schema.edgeLabel("rated")
    .sourceLabel("User").targetLabel("Movie")
    .properties("rating", "timestamp")
    .ifNotExist().create();

schema.edgeLabel("tagged")
    .sourceLabel("User").targetLabel("Movie")
    .properties("tag", "timestamp")
    .ifNotExist().create();

schema.edgeLabel("belongsTo")
    .sourceLabel("Movie").targetLabel("Genre")
    .ifNotExist().create();