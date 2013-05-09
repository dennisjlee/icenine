'use strict';

angular.module('icenine2App', ['ui.state'])
  .config(function($locationProvider, $stateProvider) {
    $locationProvider.html5Mode(false);

    $stateProvider.state('home', {
      templateUrl: 'views/home.html',
      controller: HomeCtrl,
      url: '/'
    }).state('files', {
      url: '/{type:tv|movies}{path:/.*}',
      templateUrl: 'views/files.html',
      controller: FilesCtrl
    });

  });
