'use strict';

angular.module('icenine2App').controller('FilesCtrl', FilesCtrl);

function FilesCtrl($scope, $state, $stateParams, $http, $q) {
  $scope.path = $stateParams.path; // Expected to contain leading and trailing slash
  $scope.type = $stateParams.type;

  // ignore leading and trailing slash
  var pathComponents = $scope.path.slice(1, -1).split('/');
  pathComponents.unshift($scope.type);
  var explodedComponents = [], partialPath = '';
  for (var i = 0; i < pathComponents.length; i++) {
    var name = pathComponents[i];
    if (name) {
      partialPath += '/' + name;
      explodedComponents.push({path: partialPath, name: name});
    }
  }
  $scope.explodedComponents = explodedComponents;

  var type = $scope.type == 'movies' ? 'movie' : $scope.type;
  $scope.metadata =
      $http.get('/api/metadata/' + type + $scope.path)
          .then(function(response) {
            return response.data;
          });

  var subdirsDeferred = $q.defer();
  var filesDeferred = $q.defer();
  $scope.subdirs = subdirsDeferred.promise;
  $scope.files = filesDeferred.promise;

  $scope.metadata.then(function(metadata) {
    return $http.get('/api/children/' + metadata._id)
        .then(function(response) {
          // Assume that the first elements in the children array are
          // subdirectories and the rest are files
          var children = response.data;
          for (var i = 0; i < children.length; i++) {
            if (!children[i].directory) {
              break;
            }
          }
          filesDeferred.resolve(children.splice(i));
          subdirsDeferred.resolve(children);
        });
  });

};
