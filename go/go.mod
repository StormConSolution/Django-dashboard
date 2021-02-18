module dashboard

go 1.15

replace github.com/3xian/darkseg v0.0.0-20140606144946-7e1f5876a7ad => ../repustate-api/src/github.com/3xian/darkseg

replace bitbucket.org/repustatecom/repustate-api/server/categories => ../repustate-api/server/categories

require (
	bitbucket.org/repustatecom/repustate-api/server/arabictagger v0.0.0-20210217193116-d6507cb4b920 // indirect
	bitbucket.org/repustatecom/repustate-api/server/categories v0.0.0-20210217193116-d6507cb4b920
	bitbucket.org/repustatecom/repustate-api/server/common v0.0.0-20210217193116-d6507cb4b920 // indirect
	bitbucket.org/repustatecom/repustate-api/server/customentities v0.0.0-20210217193116-d6507cb4b920 // indirect
	bitbucket.org/repustatecom/repustate-api/server/customsentiment v0.0.0-20210217193116-d6507cb4b920 // indirect
	bitbucket.org/repustatecom/repustate-api/server/deepsearch v0.0.0-20210217193116-d6507cb4b920
	bitbucket.org/repustatecom/repustate-api/server/entities v0.0.0-20210217193116-d6507cb4b920
	bitbucket.org/repustatecom/repustate-api/server/entities/util v0.0.0-20210217193116-d6507cb4b920 // indirect
	bitbucket.org/repustatecom/repustate-api/server/filter v0.0.0-20210217193116-d6507cb4b920 // indirect
	bitbucket.org/repustatecom/repustate-api/server/gofoma v0.0.0-20210217193116-d6507cb4b920 // indirect
	bitbucket.org/repustatecom/repustate-api/server/indonesiantagger v0.0.0-20210217193116-d6507cb4b920 // indirect
	bitbucket.org/repustatecom/repustate-api/server/mecab v0.0.0-20210217193116-d6507cb4b920 // indirect
	bitbucket.org/repustatecom/repustate-api/server/memcache v0.0.0-20210217193116-d6507cb4b920
	bitbucket.org/repustatecom/repustate-api/server/rdrtagger v0.0.0-20210217193116-d6507cb4b920 // indirect
	bitbucket.org/repustatecom/repustate-api/server/segmentation v0.0.0-20210217193116-d6507cb4b920 // indirect
	bitbucket.org/repustatecom/repustate-api/server/sentiment v0.0.0-20210217193116-d6507cb4b920
	bitbucket.org/repustatecom/repustate-api/server/settings v0.0.0-20210217193116-d6507cb4b920
	bitbucket.org/repustatecom/repustate-api/server/thai v0.0.0-20210217193116-d6507cb4b920 // indirect
	bitbucket.org/repustatecom/repustate-api/server/treetagger v0.0.0-20210217193116-d6507cb4b920 // indirect
	bitbucket.org/repustatecom/repustate-api/server/word2vec v0.0.0-20210217193116-d6507cb4b920 // indirect
	github.com/kr/text v0.2.0 // indirect
	github.com/lib/pq v1.9.0
	golang.org/x/sync v0.0.0-20201207232520-09787c993a3a
	golang.org/x/text v0.3.5 // indirect
)
