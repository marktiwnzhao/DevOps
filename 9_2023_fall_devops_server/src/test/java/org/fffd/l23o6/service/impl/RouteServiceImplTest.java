package org.fffd.l23o6.service.impl;

import org.fffd.l23o6.dao.RouteDao;
import org.fffd.l23o6.dao.StationDao;
import org.fffd.l23o6.dao.TrainDao;
import org.fffd.l23o6.service.RouteService;
import org.fffd.l23o6.service.StationService;
import org.fffd.l23o6.service.TrainService;
import org.junit.jupiter.api.AfterEach;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.context.SpringBootTest;

import java.util.Arrays;


@SpringBootTest
class RouteServiceImplTest {
    @Autowired
    TrainService trainService;
    @Autowired
    TrainDao trainDao;
    @Autowired
    StationDao stationDao;
    @Autowired
    RouteDao routeDao;
    @Autowired
    StationService stationService;
    @Autowired
    RouteService routeService;

    @BeforeEach
    void initStation() {
        trainDao.deleteAll();
        stationDao.deleteAll();
        routeDao.deleteAll();
        stationService.addStation("1");
        stationService.addStation("2");
        stationService.addStation("3");
        stationService.addStation("4");
        stationService.addStation("5");
        stationService.addStation("6");
        routeService.addRoute("r1", Arrays.asList(1L, 2L, 3L, 4L, 5L));
        routeService.addRoute("r2", Arrays.asList(1L, 2L, 3L, 4L, 5L));

    }

    @AfterEach
    void delAllStation() {
        trainDao.deleteAll();
    }

    @Test
    void test_1() {

    }


}