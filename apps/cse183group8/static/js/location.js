"use strict";

let app = {};


app.data = {    
    data: function() {
        return {
            chart: undefined,

            //dummy data for testing
            //top_contributors: [{name: "guy", contributions: 5}, {name: "person", contributions: 2},{name: "guy", contributions: 5}, {name: "person", contributions: 2},{name: "guy", contributions: 5}, {name: "person", contributions: 2},{name: "guy", contributions: 5}, {name: "person", contributions: 2}],
            //location_data: [{species: "White-crowned Sparrow", "day": ['2024-01-02', '2024-01-03'], count: [10, 5]}, {species: "Song Sparrow", "day": ['2024-01-02'], count: [10]}, {species: "American Crow", "day": ['2024-01-02', '2024-03-03'], count: [10, 9]}, {species: "American Crow", "day": ['2024-01-02', '2024-03-03'], count: [10, 9]}, {species: "American Crow", "day": ['2024-01-02', '2024-03-03'], count: [10, 9]}, {species: "American Crow", "day": ['2024-01-02', '2024-03-03'], count: [10, 9]}],

            top_contributors: [],
            location_data: [],

            sightings: [],
            checklist: [],

            total_sightings: 0,
            total_checklists: 0,

            //selected region coordinates
            x1: 0,
            y1: 0,

            x2: 0,
            y2: 0,

            dropdown_active: false, // dropdown to appear or not
            active_species: null, // true/false for selected bird in dropdown

            total_current_sighting: 0, //the bird that the user has selected
        };
    },
    methods: {        


        /********************
         * Draws a graph using chart.js depending on which bird is selected by user.
         * horizontal axis shows days the bird is spotted
         * vertical axis shows number of times bird is spotted
         ********************/
        make_chart: function(labels, data) {
            //destory graph if it already exists so we can reuse the canvas
            if (this.chart != undefined) {
                this.chart.destroy();
            }
            const ctx = this.$refs.speciesChart; //context
            this.chart = new Chart(ctx, {
                type: 'bar',
                data: {
                labels: labels,
                datasets: [{
                    label: '# of Times Seen', 
                    data: data,
                    borderWidth: 1
                    }]
                },
                options: {
                    scales: {
                        y: {
                        beginAtZero: true
                        }
                    },
                    animation: {
                        duration: 0      // no animation
                    }
                }
            });

        },

        /********************
         * opens or closes the dropdown menu for species selection on click
         ********************/
        click_dropdown: function() {
            this.dropdown_active = !this.dropdown_active;
        },

        /********************
         * closes the dropdown menu for species selection and
         * calls make_graph. Passes which bird is selected
         ********************/
        select_bird: function(bird) {
            this.dropdown_active = false;
            this.active_species = bird.species;

            this.make_chart(bird.day, bird.count);

            this.total_current_sighting = 0;
            for(let i = 0; i < bird['count'].length; i++) {
                this.total_current_sighting += bird['count'][i];
            }
        },

    }

    
};

app.vue = Vue.createApp(app.data).mount("#app");

app.load_data = function () {
    axios.get(get_location_data_url).then(function (r) {
        app.vue.location_data = r.data.location_data; //[{'species': 'bird', 'day': ['2021-02-03'], 'count': [2]}]
        app.vue.top_contributors = r.data.contributor_list; //[{'name': name, 'contributions': 1}]
        app.vue.total_sightings = r.data.total_sightings;
        app.vue.total_checklists = r.data.total_checklists;

        console.log(app.vue.location_data);
    });


}

app.load_data();

