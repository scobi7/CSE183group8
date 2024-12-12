"use strict";

let app = {};

app.data = {
  data: function () {
    return {
      checklists: [], // Holds bird data
    };
  },
  methods: {
    loadChecklists: function () {
      axios
        .get(load_checklists_url) // Fetch data from the backend
        .then((response) => {
          this.checklists = response.data.checklists;
          this.plotBirdsOnMap(); // Plot the bird data on the map
        })
        .catch((error) => {
          console.error("Error loading checklists:", error);
        });
    },
    plotBirdsOnMap: function () {
      if (this.checklists.length > 0) {
        this.checklists.forEach((bird) => {
          if (bird.LATITUDE && bird.LONGITUDE) {
            L.marker([bird.LATITUDE, bird.LONGITUDE])
              .addTo(this.map)
              .bindPopup(
                `<b>${bird.COMMON_NAME || "Unknown"}</b><br>
                 Observation Count: ${bird.OBSERVATION_COUNT || 0}<br>
                 Date: ${bird.OBSERVATION_DATE}<br>
                 Duration: ${bird.DURATION_MINUTES} minutes`
              );
          }
        });
      }
    },
  },
  mounted: function () {
    this.map = L.map("map").setView([37.7749, -122.4194], 10); // Default location (San Francisco)
    L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
      attribution: "&copy; OpenStreetMap contributors",
    }).addTo(this.map);

    this.loadChecklists(); // Load bird data
  },
};

Vue.createApp(app.data).mount("#app");

