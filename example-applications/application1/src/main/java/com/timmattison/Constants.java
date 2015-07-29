package com.timmattison;

import java.security.SecureRandom;

public class Constants {
    private static final SecureRandom secureRandom = new SecureRandom();
    public static final long randomLong = Math.abs(secureRandom.nextLong());
}
