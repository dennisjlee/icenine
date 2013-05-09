'use strict';

angular.module('icenine2App').controller('MainCtrl', MainCtrl);
  
function MainCtrl($state, $scope) {
  $state.transitionTo('home');
};
