package main

import (
	"bufio"
	"fmt"
	"io/ioutil"
	"os"
	"regexp"
	"runtime"
	"strings"
	"sync"
)

// TODO this program isn't exactly right yet but gives the idea

func main() {
	numCPU := runtime.NumCPU()
	fmt.Printf("Reading list of files to check from stdin. Using %d cores.\n", numCPU)

	// files := make(chan string)
	var files []string
	scanner := bufio.NewScanner(os.Stdin)
	for scanner.Scan() {
		// files <- scanner.Text()
		files = append(files, scanner.Text())
	}
	if scanner.Err() != nil {
		panic("scanner error")
	}

	var chunks [][]string
	chunkSize := (len(files) + numCPU - 1) / numCPU
	for i := 0; i < len(files); i += chunkSize {
		end := i + chunkSize
		if end > len(files) {
			end = len(files)
		}
		chunks = append(chunks, files[i:end])
	}

	errs := make(chan int, len(files))
	var wg sync.WaitGroup
	// for i := 0; i < runtime.NumCPU(); i++ {
	for _, chunk := range chunks {
		wg.Add(1)
		go func() {
			defer wg.Done()
			for _, f := range chunk {
				if !check(f) {
					errs <- 1
				}
			}
		}()
	}
	wg.Wait()

	select {
	case _ = <-errs:
		os.Exit(1)
	default:
		// nothing in chan, all's well
	}
}

func check(file string) bool {
	data, err := ioutil.ReadFile(file)
	if err != nil {
		panic(err)
	}
	html := string(data) // TODO decoding?

	// remove everything before <h1
	h1 := strings.Index(html, "<h1")
	if h1 == -1 {
		h1 = 0
	}
	html = html[h1:]

	// add newlines after each closing script tag to avoid greedy matching
	strings.ReplaceAll(html, "</script>", "</script>\n")

	// remove scripts.
	re := regexp.MustCompile(`<script.*</script>`)
	html = re.ReplaceAllLiteralString(html, "")

	// remove rest of html tags
	rehtml := regexp.MustCompile(`<[^>]*>`)
	html = rehtml.ReplaceAllLiteralString(html, "")

	ok := true

	keywords := []string{"Logging without Limits", "Traces without Limits", "Metrics without Limits", "Log Rehydration"}
	for _, kw := range keywords {
		i := strings.Index(html, kw)
		if i == -1 {
			// fmt.Printf("Didn't find keyword %s\n", kw)
			continue
		}
		after := i + len(kw)
		charsAfter := html[after : after+7]
		if strings.HasPrefix(charsAfter, "™") || strings.HasPrefix(charsAfter, "&trade") || strings.HasPrefix(charsAfter, " &trade") {
			// fmt.Printf("%s ok\n", kw)
			continue
		}
		longForm := kw + " is a trademark of Datadog, Inc."
		if strings.Contains(html, longForm) {
			// fmt.Printf("%s ok\n", kw)
			continue
		}
		fmt.Printf("%s is missing trademark for %s\n", file, kw)
		ok = false
	}

	return ok
}
