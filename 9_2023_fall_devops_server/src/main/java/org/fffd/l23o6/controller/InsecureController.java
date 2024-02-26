package org.fffd.l23o6.controller;

import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;

@RestController
public class InsecureController {

    @GetMapping("/insecure")
    public String insecureEndpoint(@RequestParam String input) {
        String query = "SELECT * FROM users WHERE username = '" + input + "';";
        return query;
    }
}