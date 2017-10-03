/**
 * Created by Javora Gabor on 2017. 09. 05..
 */
var app = angular.module("MEnetrend", ["ui.router"]);

app.config(function ($stateProvider, $urlRouterProvider) {

    $urlRouterProvider.otherwise('/error-404');

    $stateProvider
        .state("/", {
            url: "",
            templateUrl: "/static/partials/home.html"
        })
        .state("/listRoutes", {
            url: "/list-routes",
            templateUrl: "/static/partials/list-routes.html",
            controller: "listRoutesController"
        })
        .state("/trip", {
            url: "/trip/{trip_id:int}",
            templateUrl: "/static/partials/trip.html",
            controller: "tripController"
        })
        .state("/schedule", {
            url: "/schedule/:route_short_name/{direction_id:int}",
            templateUrl: "/static/partials/schedule.html",
            controller: "scheduleController"
        })
        .state("/error-404", {
            url: "/error-404",
            templateUrl: "/static/partials/error-404.html"
        })
});


app.controller("listRoutesController", function ($scope, $http) {
    $scope.loading = true;
    $http.get("/get_tram_routes").then(function (response) {
        $scope.tram_routes = response.data;
    });

    $http.get("/get_bus_routes").then(function (response) {
        $scope.bus_routes = response.data;
    }).finally(function () {
        $scope.loading = false;
    });


    $scope.busTableOrderBy = "+route_short_name";
    $scope.busTableOrderByName = function () {
        if ($scope.busTableOrderBy === "+route_short_name") {
            $scope.busTableOrderBy = "-route_short_name";
        }
        else {
            $scope.busTableOrderBy = "+route_short_name";
        }
    };
    $scope.busTableOrderByStart = function () {
        if ($scope.busTableOrderBy === "+route_start_stop_name") {
            $scope.busTableOrderBy = "-route_start_stop_name";
        }
        else {
            $scope.busTableOrderBy = "+route_start_stop_name";
        }
    };
    $scope.busTableOrderByEnd = function () {
        if ($scope.busTableOrderBy === "+route_end_stop_name") {
            $scope.busTableOrderBy = "-route_end_stop_name";
        }
        else {
            $scope.busTableOrderBy = "+route_end_stop_name";
        }
    };

    $scope.busTableSearch = function (row) {
        return (angular.lowercase(row.route_short_name).indexOf(angular.lowercase($scope.busTableQuery) || '') !== -1 ||
            angular.lowercase(row.route_start_stop_name).indexOf(angular.lowercase($scope.busTableQuery) || '') !== -1 ||
            angular.lowercase(row.route_end_stop_name).indexOf(angular.lowercase($scope.busTableQuery) || '') !== -1);
    };

    $scope.tramTableOrderBy = "+route_short_name";
    $scope.tramTableOrderByName = function () {
        if ($scope.tramTableOrderBy === "+route_short_name") {
            $scope.tramTableOrderBy = "-route_short_name";
        }
        else {
            $scope.tramTableOrderBy = "+route_short_name";
        }
    };
    $scope.tramTableOrderByStart = function () {
        if ($scope.tramTableOrderBy === "+route_start_stop_name") {
            $scope.tramTableOrderBy = "-route_start_stop_name";
        }
        else {
            $scope.tramTableOrderBy = "+route_start_stop_name";
        }
    };
    $scope.tramTableOrderByEnd = function () {
        if ($scope.tramTableOrderBy === "+route_end_stop_name") {
            $scope.tramTableOrderBy = "-route_end_stop_name";
        }
        else {
            $scope.tramTableOrderBy = "+route_end_stop_name";
        }
    };

    $scope.tramTableSearch = function (row) {
        return (angular.lowercase(row.route_short_name).indexOf(angular.lowercase($scope.tramTableQuery) || '') !== -1 ||
            angular.lowercase(row.route_start_stop_name).indexOf(angular.lowercase($scope.tramTableQuery) || '') !== -1 ||
            angular.lowercase(row.route_end_stop_name).indexOf(angular.lowercase($scope.tramTableQuery) || '') !== -1);
    };
});

app.controller("tripController", function ($scope, $http, $state, $stateParams) {

    $http.get("/get_trip_stops", {
        params: {trip_id: $stateParams.trip_id}
    }).then(function (response) {
            $scope.trip = response.data;
        },
        function () {
            $state.go("/error-404");
        }
    );

});

app.controller("scheduleController", function ($scope, $http, $state, $stateParams, $rootScope) {

    $http.get("/get_dates").then(function (response) {
        $scope.dates = response.data;
    });

    if ($rootScope.selectedDate === undefined) {
        var date = new Date();
        var dateString = date.getFullYear() + '-'
            + ('0' + (date.getMonth() + 1)).slice(-2) + '-'
            + ('0' + date.getDate()).slice(-2);
    }
    else {
        dateString = $rootScope.selectedDate;
    }

    $scope.selectedDate = dateString;

    $http.get("/get_start_times", {
        params: {
            route_short_name: $stateParams.route_short_name,
            direction_id: $stateParams.direction_id,
            date: dateString
        }
    }).then(function (response) {
            $scope.statusCode = response.status;
            $scope.trips = response.data;
        },
        function (response) {
            $scope.statusCode = response.status;
            $scope.trips = response.data;
            if ($scope.statusCode === 404) {
                $state.go("/error-404");
            }
        }
    );

    $scope.changeDate = function (selectedDate) {
        $rootScope.selectedDate = selectedDate;
        $http.get("/get_start_times", {
            params: {
                route_short_name: $stateParams.route_short_name,
                direction_id: $stateParams.direction_id,
                date: selectedDate
            }
        }).then(function (response) {
                $scope.statusCode = response.status;
                $scope.trips = angular.copy(response.data);
            },
            function (response) {
                $scope.statusCode = response.status;
                $scope.trips = response.data;
                if ($scope.statusCode === 404) {
                    $state.go("/error-404");
                }
            }
        );
    };

});
