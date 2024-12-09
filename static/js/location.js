"use strict";

// This will be the object that will contain the Vue attributes
// and be used to initialize it.
let app = {};


app.data = {    
    data: function() {
        return {
            chart: null,
            
        };
    },
    methods: {
        // Complete as you see fit.
        my_function: function() {
            // This is an example.
            this.my_value += 1;
        },
        
        // TODO need to fetch the list of Species in the Selected Region
        // TODO need to fetch the total number of sightings in Selected Region

        // TODO need to fetch some information on top contributors for the Selected Region. (maybe total # of contributions)

        // TODO display chart by which species that user clicks
        make_chart: function() {
            const ctx = this.$refs.speciesChart;

            this.chart = new Chart(ctx, {
                type: 'bar',
                data: {
                labels: ['day 1?', 'day 2', 'day 3', 'day 4', 'day 5', 'day 6'],
                datasets: [{
                    label: '# of Times Seen',
                    data: [12, 19, 3, 5, 2, 3],
                    borderWidth: 1
                    }]
                },
                options: {
                    scales: {
                        y: {
                        beginAtZero: true
                        }
                    }
                }
            });
        }
    }

    
};

app.vue = Vue.createApp(app.data).mount("#app");

app.load_data = function () {
    axios.get(my_callback_url).then(function (r) {
        app.vue.my_value = r.data.my_value;
    });
}

app.load_data();

