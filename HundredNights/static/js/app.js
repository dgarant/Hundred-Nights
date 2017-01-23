var app = angular.module("HNights", ["ngRoute"]);

angular.isEmptyLike = function(v) {
    return (v == undefined) || (v == null) || (v == "") || (v == []);
}

app.config(["$routeProvider", function($routeProvider) {
    $routeProvider.when("/",
            {
                controller: "VisitorLookupController",
                templateUrl : "/static/partials/visitor-lookup.html"
            }).otherwise({redirectTo: "/"});
}]);

app.controller("VisitorLookupController", ["$scope", "$http", function($scope, $http) {
    $scope.isEmptyLike = angular.isEmptyLike;

    $scope.search = function() {
        $http.get("/api/visitor-search/", {params: {"name" : $scope.searchKey}}).then(function(results) {
            $scope.visitors = results.data;
        }, function(err) {
            $scope.error = err.statusText;
        });
    }

    $scope.delete = function(visitor) {
        var confirmation = confirm("Are you sure you want to delete " + visitor.name + "?");
        if(confirmation) {
            $http.get("/delete-visitor/" + visitor.id).then(function(result) { 
                    $scope.visitors = _.without($scope.visitors, visitor);
                },
                function(err) {
                    $scope.error = err.statusText;
                });

        }
    }
}]);





