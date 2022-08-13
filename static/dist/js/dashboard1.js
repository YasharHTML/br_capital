$(function() {
    "use strict";
    // Dashboard 1 Morris-chart
    Morris.Area({
        element: 'morris-area-chart',
        data: [{
            period: '2016',
            Startup: 0,
            Company: 0,
            itouch: 0
        }, {
            period: '2017',
            Startup: 130,
            Company: 100,
            itouch: 80
        }, {
            period: '2018',
            Startup: 80,
            Company: 60,
            itouch: 70
        }, {
            period: '2019',
            Startup: 70,
            Company: 200,
            itouch: 140
        }, {
            period: '2020',
            Startup: 180,
            Company: 150,
            itouch: 140
        }, {
            period: '2021',
            Startup: 105,
            Company: 100,
            itouch: 80
        }, {
            period: '2022',
            Startup: 250,
            Company: 150,
            itouch: 200
        }],
        xkey: 'period',
        ykeys: ['Startup', 'Company'],
        labels: ['Startup', 'Company'],
        pointSize: 0,
        fillOpacity: 0,
        pointStrokeColors: ['#f62d51', '#7460ee', '#009efb'],
        behaveLikeLine: true,
        gridLineColor: '#f6f6f6',
        lineWidth: 1,
        hideHover: 'auto',
        lineColors: ['#009efb', '#7460ee', '#009efb'],
        resize: true
    });

});