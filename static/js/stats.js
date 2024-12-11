"use strict";

// Vue application setup
const statsApp = {
  data() {
    return {
      myValue: 1,
      commonNames: [],
      query: "",
      searchOption: "recent",
    };
  },
  methods: {
    toggleSearchOption() {
      this.searchOption = this.searchOption === "recent" ? "old" : "recent";
      console.log("Search option toggled to:", this.searchOption);
    },
    async search() {
      console.log("Search function called");
      console.log("Query:", this.query);

      try {
        if (this.query.length >= 1) {
          const response = await axios.post(search_url, {
            params: { q: this.query, option: this.searchOption },
          });
          this.commonNames = response.data.common_names.map((name) => ({
            ...name,
            observation_dates: [],
          }));
          console.log("Common names updated:", this.commonNames);
        } else {
          const response = await axios.get(load_user_statistics_url);
          this.commonNames = response.data.common_names;
          console.log("All names fetched:", this.commonNames);
        }
      } catch (error) {
        console.error("Error in search:", error);
      }
    },
    async fetchObservationDates(name) {
      console.log("Fetching observations for:", name.COMMON_NAME);
      try {
        const response = await axios.post(observation_dates_url, {
          common_name: name.COMMON_NAME,
        });
        name.observation_dates = response.data.observation_dates;
        console.log("Observation dates fetched:", name.observation_dates);
      } catch (error) {
        console.error("Error fetching observation dates:", error);
      }
    },
    async moveMapToObservation(name, date = null) {
      console.log("Moving map to observation for:", name.COMMON_NAME);
      const payload = { common_name: name.COMMON_NAME };
      if (date) {
        payload.observation_date = date.OBSERVATION_DATE;
      }

      try {
        const response = await axios.post(observation_dates_url, payload);
        const mostRecentSighting = response.data.most_recent_sighting;

        if (mostRecentSighting?.LATITUDE && mostRecentSighting?.LONGITUDE) {
          const { LATITUDE, LONGITUDE } = mostRecentSighting;
          window.map.setView([LATITUDE, LONGITUDE], 13);
          L.marker([LATITUDE, LONGITUDE])
            .addTo(window.map)
            .bindPopup(name.COMMON_NAME)
            .openPopup();
          console.log("Map moved to:", { LATITUDE, LONGITUDE });
        } else {
          console.error("Invalid location data:", mostRecentSighting);
        }
      } catch (error) {
        console.error("Error moving map to observation:", error);
      }
    },
  },
  async mounted() {
    console.log("Vue app mounted. Loading initial data...");
    try {
      const response = await axios.get(load_user_statistics_url);
      this.commonNames = response.data.common_names;
      console.log("Initial data loaded:", this.commonNames);
    } catch (error) {
      console.error("Error loading initial data:", error);
    }
  },
};

// Mount the Vue app
Vue.createApp(statsApp).mount("#statistics-app");
