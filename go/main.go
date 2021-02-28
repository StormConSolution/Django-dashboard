package main

import (
	"database/sql"
	"encoding/csv"
	"fmt"
	"log"
	"os"
	"strconv"
	"sync"

	_ "github.com/lib/pq"
	"golang.org/x/sync/errgroup"

	"bitbucket.org/repustatecom/repustate-api/server/categories"
	dbpedia "bitbucket.org/repustatecom/repustate-api/server/deepsearch/dbpedia/api"
	"bitbucket.org/repustatecom/repustate-api/server/deepsearch/geolocation"
	"bitbucket.org/repustatecom/repustate-api/server/entities"
	"bitbucket.org/repustatecom/repustate-api/server/memcache"
	"bitbucket.org/repustatecom/repustate-api/server/sentiment"
	"bitbucket.org/repustatecom/repustate-api/server/sentiment/helper"
	"bitbucket.org/repustatecom/repustate-api/server/settings"
)

func main() {
	settings.InitLanguages()

	var g errgroup.Group

	// Load the entity, sentiment and the part of speech models.
	g.Go(func() error {
		return memcache.PopulateCaches(true, memcache.Memory)
	})

	g.Go(func() error {
		return entities.LoadLinkIndex()
	})

	g.Go(func() error {
		return entities.LoadThemes()
	})

	g.Go(func() error {
		return entities.LoadNames()
	})

	g.Go(func() error {
		return geolocation.LoadLocations()
	})

	g.Go(func() error {
		return dbpedia.LoadInterlanguageData()
	})

	var wg sync.WaitGroup

	for _, lang := range settings.GetLanguages() {
		log.Println("Loading data models for", lang, "...")
		l := lang
		wg.Add(1)
		go func(wg *sync.WaitGroup) {
			defer wg.Done()
			helper.LoadLanguage(l)
		}(&wg)
	}

	wg.Wait()

	// Wait for all languages to load.
	if err := g.Wait(); err != nil {
		log.Fatal(err)
	}

	dsn := "user=martin dbname=dashboard sslmode=disable host=localhost port=5432 password=Moju1981!"
	db, err := sql.Open("postgres", dsn)
	if err != nil {
		log.Fatal(err)
	}

	rows, err := db.Query("select id, text, language from data_data where project_id = 3155 and language in ('en', 'fr', 'ru', 'tr', 'ko', 'zh')")
	if err != nil {
		log.Fatal(err)
	}
	defer rows.Close()

	var id int
	var text, lang string

	fd, err := os.Create("aspects.csv")
	if err != nil {
		log.Fatal(err)
	}

	w := csv.NewWriter(fd)
	defer w.Flush()

	i := 0

	for rows.Next() {
		rows.Scan(&id, &text, &lang)

		if i%100 == 0 {
			log.Println(i)
			w.Flush()
		}
		i++

		entitiesFound, _, err := entities.Extract("xxx", text, lang)
		if err != nil {
			log.Println(err)
			continue
		}

		scoredChunks, err := helper.GetSentimentByChunks("xxx", lang, text, sentiment.DefaultPolarityFunc)
		if err != nil {
			log.Println(err)
			continue
		}

		for _, scoredChunk := range scoredChunks {

			matches, err := categories.Classify(
				scoredChunk,
				entitiesFound,
				"rolex",
				lang,
				text,
			)

			if err != nil {
				log.Println(err)
				continue
			}

			for _, m := range matches {
				w.Write([]string{
					strconv.Itoa(id),
					m.Aspect,
					m.Fragment,
					fmt.Sprintf("%f", scoredChunk.Score),
					m.Topic,
					"{" + m.Qualifier + "}"},
				)
			}
		}
	}
}
