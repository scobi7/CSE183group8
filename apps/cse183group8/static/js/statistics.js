"use strict";

// Initialize Vue application
const statsApp = Vue.createApp({
    data() {
        return {
            my_value: 1,
            common_names: [],
            query: "",
            search_option: "recent",
        };
    },
    methods: {
        updateSearchOption() {
            this.search_option = this.search_option === "recent" ? "old" : "recent";
            console.log("Changing search option to:", this.search_option);
        },
        search() {
            console.log("Search function called with query:", this.query);

            if (this.query.length >= 1) {
                axios.post(search_url, { params: { q: this.query, option: this.search_option } })
                    .then(response => {
                        this.common_names = response.data.common_names.map(name => ({
                            ...name,
                            observation_dates: [], 
                        }));
                        console.log("Common names updated:", this.common_names);
                    })
                    .catch(error => {
                        console.error("Error during search:", error);
                    });
            } else {
                this.loadCommonNames(); 
            }
        },
        fetchObservationDates(name) {
            console.log("Fetching observation dates for:", name.COMMON_NAME);

            axios.post(observation_dates_url, { common_name: name.COMMON_NAME })
                .then(response => {
                    name.observation_dates = response.data.observation_dates;
                    console.log("Observation dates updated for:", name.COMMON_NAME, name.observation_dates);
                })
                .catch(error => {
                    console.error("Error fetching observation dates:", error);
                });
        },
        moveMapToObservation(name, date = null) {
            // Move the map to the most recent observation location
            console.log("Moving map to observation for:", name.COMMON_NAME);

            const payload = { common_name: name.COMMON_NAME };
            if (date) {
                payload.observation_date = date.OBSERVATION_DATE;
            }

            axios.post(observation_dates_url, payload)
                .then(response => {
                    const mostRecentSighting = response.data.most_recent_sighting;
                    console.log("Most recent sighting:", mostRecentSighting);

                    if (mostRecentSighting && mostRecentSighting.LATITUDE && mostRecentSighting.LONGITUDE) {
                        window.map.setView([mostRecentSighting.LATITUDE, mostRecentSighting.LONGITUDE], 13);
                        L.marker([mostRecentSighting.LATITUDE, mostRecentSighting.LONGITUDE]).addTo(window.map)
                            .bindPopup(name.COMMON_NAME)
                            .openPopup();
                    } else {
                        console.error("Invalid location data:", mostRecentSighting);
                    }
                })
                .catch(error => {
                    console.error("Error fetching most recent sighting:", error);
                });
        },
        loadCommonNames() {
            console.log("Loading common names...");
            axios.get(load_user_statistics_url)
                .then(response => {
                    this.common_names = response.data.common_names;
                    console.log("Common names loaded:", this.common_names);
                })
                .catch(error => {
                    console.error("Error loading common names:", error);
                });
        },
    },
    mounted() {
        this.loadCommonNames();
    },
});

// Mount the Vue application to the DOM element
statsApp.mount("#statistics-app");
