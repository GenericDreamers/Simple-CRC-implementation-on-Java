package Java.CNDC;

public enum predefinedCRC {
    CUSTOM("Custom CRC",""),
    CRC8("CRC-8","111010101"),
    CRC8Bluetooth("CRC-8-Bluetooth","110100111"),
    CRC8CCITT("CRC-8-CCITT","100000111"),
    CRC12("CRC-12","1100000001111"),
    CRC16CCITT("CRC-16-CCITT","10001000000100001"),
    CRC24("CRC-24","1010111010110110111001011"),
    CRC32("CRC-32","100000100110000010001110110110111"),
    CRC64ISO("CRC-64-ISO","10000000000000000000000000000000000000000000000000000000000011011");

    private final String name;
    private final String poly;

    predefinedCRC(String name, String poly) {
        this.name = name;
        this.poly = poly;
    }

    @Override public String toString() { return name; }
    public String getPoly() {return poly;}
}
