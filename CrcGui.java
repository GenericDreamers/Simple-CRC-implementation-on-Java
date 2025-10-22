package Java.CNDC;

import javax.swing.*;
import javax.swing.border.LineBorder;
import java.awt.*;
import java.awt.event.FocusAdapter;
import java.awt.event.FocusEvent;
import java.util.*;

public class CrcGui extends JFrame {
    private final JTextArea inputArea = new JTextArea(8, 60);
    private final JTextField polyField = new JTextField(20);
    private final JTextArea outputArea = new JTextArea(10, 60);
    private final JButton inputModeBtn = new JButton("Input mode: Binary");
    private boolean asciiMode = false;
    private final String INPUT_PLACEHOLDER = "Input goes here...";
    private final String OUTPUT_PLACEHOLDER = "Output goes here...";
    private final JComboBox<predefinedCRC> crcTypeCombo = new JComboBox<>(predefinedCRC.values());
    private final JRadioButton lookupOn = new JRadioButton("Yes");
    private final JRadioButton lookupOff = new JRadioButton("No", true);
    private final JPanel notDivByXLight;
    private final JPanel divByXPlus1Light;

    public CrcGui() {
        super("CRC Simulator");
        setDefaultCloseOperation(JFrame.EXIT_ON_CLOSE);
        setLayout(new BorderLayout(6, 6));

        JScrollPane inScroll = new JScrollPane(addPlaceholder(inputArea, INPUT_PLACEHOLDER));
        inScroll.setBorder(BorderFactory.createTitledBorder("Input Data"));

        outputArea.setEditable(false);
        JScrollPane outScroll = new JScrollPane(addPlaceholder(outputArea, OUTPUT_PLACEHOLDER));
        outScroll.setBorder(BorderFactory.createTitledBorder("Output / Log"));

        JPanel genRow = new JPanel(new FlowLayout(FlowLayout.LEFT));
        genRow.add(new JLabel("Generator Polynomial (binary):"));
        genRow.add(polyField);
        notDivByXLight = createLightPanel("Not divisible by x");
        divByXPlus1Light = createLightPanel("Divisible by x+1");
        genRow.add(notDivByXLight);
        genRow.add(divByXPlus1Light);
        notDivByXLight.setToolTipText("Checks if the polynomial is not divisible by x (constant term is 1)");
        divByXPlus1Light.setToolTipText("Checks if the polynomial is divisible by x+1 (even number of 1s)");

        JPanel crcSelectPanel = new JPanel(new FlowLayout(FlowLayout.LEFT));
        crcSelectPanel.add(new JLabel("Predefined CRC:"));
        crcSelectPanel.add(crcTypeCombo);
        crcSelectPanel.add(new JLabel("Use Lookup Table:"));
        ButtonGroup lookupGroup = new ButtonGroup();
        lookupGroup.add(lookupOn); lookupGroup.add(lookupOff);
        crcSelectPanel.add(lookupOn); crcSelectPanel.add(lookupOff);

        crcTypeCombo.addActionListener(e -> {
            predefinedCRC selected = (predefinedCRC) crcTypeCombo.getSelectedItem();
            if (selected != null && selected != predefinedCRC.CUSTOM) {
                polyField.setText(selected.getPoly());
                updateLights();
            }
        });

        polyField.addFocusListener(new FocusAdapter() {
            @Override
            public void focusLost(FocusEvent e) {
                updateLights();
                predefinedCRC selected = (predefinedCRC) crcTypeCombo.getSelectedItem();
                if (selected != null && selected != predefinedCRC.CUSTOM && !Objects.equals(polyField.getText(), selected.getPoly())) {
                    crcTypeCombo.setSelectedItem(predefinedCRC.CUSTOM); //If there is a change in polyField, set CRC combo box to CUSTOM
                }
            }
        });

        JPanel buttons = new JPanel(new FlowLayout(FlowLayout.LEFT));
        buttons.add(inputModeBtn);
        JButton encodeBtn = new JButton("Encode");
        buttons.add(encodeBtn);
        JButton checkBtn = new JButton("Decode");
        buttons.add(checkBtn);
        JButton simulateErrorBtn = new JButton("Simulate Error");
        buttons.add(simulateErrorBtn);
        JButton clearBtn = new JButton("Clear All");
        buttons.add(clearBtn);

        JPanel topPanel = new JPanel(new BorderLayout(6, 6));
        topPanel.add(inScroll, BorderLayout.CENTER);
        topPanel.add(buttons, BorderLayout.SOUTH);
        JPanel topNorth = new JPanel(new GridLayout(2, 1));
        topNorth.add(crcSelectPanel);
        topNorth.add(genRow);
        topPanel.add(topNorth, BorderLayout.NORTH);

        JSplitPane splitPane = new JSplitPane(JSplitPane.VERTICAL_SPLIT, topPanel, outScroll);
        splitPane.setDividerLocation(300);
        splitPane.setResizeWeight(0.6);
        splitPane.setOneTouchExpandable(true);
        add(splitPane, BorderLayout.CENTER);

        encodeBtn.addActionListener(e -> filterInvalidInputsAndAction(1));
        checkBtn.addActionListener(e -> filterInvalidInputsAndAction(2));
        inputModeBtn.addActionListener(e -> toggleAsciiMode());
        simulateErrorBtn.addActionListener(e -> simulateError());
        clearBtn.addActionListener(e -> {
            inputArea.setText(INPUT_PLACEHOLDER);
            outputArea.setText(OUTPUT_PLACEHOLDER);
            polyField.setText("");
            crcTypeCombo.setSelectedItem(predefinedCRC.CUSTOM);
        });

        pack();
        setLocationRelativeTo(null);
        setVisible(true);
    }

    // --- CRC Core ---
    private String encodeBitwise(String data, String polyBits, int width) {
        int pad = width - 1;
        StringBuilder augmented = new StringBuilder(data);
        augmented.append("0".repeat(pad));

        int stop = augmented.length() - pad;
        for (int i = 0; i < stop; i++) {
            if (augmented.charAt(i) != '1') continue;
            for (int j = 0; j < width; j++) {
                if (polyBits.charAt(j) == '1') {
                    int idx = i + j;
                    char newBit = (augmented.charAt(idx) == '1') ? '0' : '1';
                    augmented.setCharAt(idx, newBit);
                }
            }
        }
        String remainder = augmented.substring(augmented.length() - pad);
        return data + remainder;
    }

    private boolean decodeBitwise(String codeword, String polyBits, int width) {
        int pad = Math.max(0, width - 1);
        StringBuilder temp = new StringBuilder(codeword);
        int stop = temp.length() - pad;
        for (int i = 0; i < stop; i++) {
            if (temp.charAt(i) != '1') continue;
            for (int j = 0; j < width; j++) {
                if (polyBits.charAt(j) == '1') {
                    int idx = i + j;
                    char newBit = (temp.charAt(idx) == '1') ? '0' : '1';
                    temp.setCharAt(idx, newBit);
                }
            }
        }
        for (int i = stop; i < temp.length(); i++) if (temp.charAt(i) != '0') return false;
        return true;
    }

    private String[] buildCrcTable(String polyBits, int width) {
        String[] table = new String[256];
        int SBLength = Math.max(8, width - 1);

        for (int i = 0; i < 256; i++) {
            StringBuilder crc = new StringBuilder("0".repeat(SBLength));
            for (int bit = 0; bit < 8; bit++) {
                if (((i >> (7 - bit)) & 1) == 1) {
                    crc.setCharAt(bit, '1');
                }
            } //This loop essentially converts int i into an 8-bit byte

            // perform 8 MSB-first bit shifts with conditional XOR by polynomial (excluding implicit top bit)
            for (int step = 0; step < 8; step++) {
                boolean topSet = crc.charAt(0) == '1';
                // left shift CRC by 1
                crc.deleteCharAt(0);
                crc.append('0');

                if (topSet) {
                    StringBuilder next = new StringBuilder(SBLength);
                    for (int k = 0; k < SBLength; k++) {next.append(polyBits.charAt(k+1) == crc.charAt(k) ? '0' : '1');}
                    crc = next;
                }
            }
            table[i] = crc.toString();
        }
        return table;
    }

    /**
     * This method uses the concept of the CRC register, and processes the message byte-by-byte instead of bit-by-bit.
     * As such, CRC-7 and below are NOT supported, and the encoded data length MUST be a multiple of 8 bits.
     * @param data The data to encode. If data length is not a multiple of 8, the last few least significant bits are right-padded into a byte.
     * @param polyBits The generator polynomial (in binary, with implicit 1 written down).
     *                 Only supports CRC-8 or higher (width >= 9)
     * @param width The length of the generator polynomial.
     * @return The original data + CRC appended at the end.
     */
    private String encodeLookup(String data, String polyBits, int width) {
        String[] table = buildCrcTable(polyBits, width);
        int padBits = width - 1;
        StringBuilder crc = new StringBuilder("0".repeat(padBits));
        // process message bytes in 8-bit chunks
        for (int i = 0; i < data.length(); i += 8) {
            int take = Math.min(8, data.length() - i);
            String byteStr = data.substring(i, i + take);
            if (take < 8) {
                byteStr = byteStr + "0".repeat(8 - take); // right-pad
            }

            String top8 = crc.substring(0, 8);
            StringBuilder idxBits = new StringBuilder(8);
            for (int k = 0; k < 8; k++) idxBits.append(top8.charAt(k) == byteStr.charAt(k) ? '0' : '1');
            int idx = Integer.parseInt(idxBits.toString(), 2); //find index for CRC table

            StringBuilder newCrc = new StringBuilder(padBits);
            crc.delete(0,8);
            crc.append("0".repeat(8)); //left shift old CRC by 8 (removing the bits used to find the table index)
            String tb = table[idx];
            for (int k = 0; k < padBits; k++) newCrc.append(tb.charAt(k) == crc.charAt(k) ? '0' : '1'); //XOR
            crc = newCrc;
        }
        return data + crc;
    }

    private boolean decodeLookup(String codeword, String polyBits, int width) {
        String[] table = buildCrcTable(polyBits, width);
        int padBits = width - 1;
        StringBuilder crc = new StringBuilder("0".repeat(padBits));

        for (int i = 0; i < codeword.length(); i += 8) {
            int take = Math.min(8, codeword.length() - i);
            String byteStr = codeword.substring(i, i + take);
            if (take < 8) {
                byteStr = byteStr + "0".repeat(8 - take); // right-pad
            }

            String top8 = crc.substring(0, 8);
            StringBuilder idxBits = new StringBuilder(8);
            for (int k = 0; k < 8; k++) idxBits.append(top8.charAt(k) == byteStr.charAt(k) ? '0' : '1');
            int idx = Integer.parseInt(idxBits.toString(), 2);

            StringBuilder newCrc = new StringBuilder(padBits);
            crc.delete(0,8);
            crc.append("0".repeat(8)); //left shift CRC by 8
            String tb = table[idx];
            for (int k = 0; k < width - 1; k++) newCrc.append(tb.charAt(k) == crc.charAt(k) ? '0' : '1');
            crc = newCrc;
        }
        // valid if register is all zeros
        return crc.lastIndexOf("1") == -1;
    }

    private void filterInvalidInputsAndAction(int mode) {
        String poly = removeWhitespace(polyField.getText());
        if (poly.isEmpty()) {
            showError("Polynomial field is empty.");
            return;
        }
        String error = validatePoly(poly);
        if (!error.isEmpty()) {
            showError(error);
            return;
        }

        String data = inputArea.getText().trim();
        if (data.isEmpty() || data.equals(INPUT_PLACEHOLDER)) {
            showError("Input field is empty.");
            return;
        }
        if (asciiMode) {
            try {
                data = asciiToBinary(data);
                toggleAsciiMode(); //turn off ASCII mode after conversion
            } catch (IllegalArgumentException ex) {
                showError(ex.getMessage());
                return;
            }
        }
        if (!data.matches("[01]+")) {
            showError("Input must be binary (0/1) or use ASCII mode.");
            return;
        }

        String selectedCrc = crcTypeCombo.getSelectedItem().toString();
        boolean useLookup = lookupOn.isSelected();
        int polyLength = poly.length();
        if (useLookup) {
            if (polyLength <= 8) {
                showError("CRC lookup table only supports CRC-8 and above. Choose a different polynomial or turn off lookup.");
                return;
            }
            if (data.length() % 8 != 0) {
                int choice = JOptionPane.showConfirmDialog(
                        this,
                        "Your input length is NOT a multiple of 8 bits. As such, the input will have right-padded with zeroes to work with the CRC lookup table." +
                                "\nThis may alter the results of the encoding and decoding process. Proceed?",
                        "Warning",
                        JOptionPane.YES_NO_OPTION,
                        JOptionPane.WARNING_MESSAGE
                );
                if (choice == JOptionPane.NO_OPTION || choice == JOptionPane.CLOSED_OPTION) {
                    return;
                }
                //Yes
                int lastByte = data.length()/8;
                int bits = data.length() - lastByte*8;
                String unfinishedByte = data.substring(lastByte*8) + "0".repeat(8 - bits);
                data = data.substring(0, lastByte*8) + unfinishedByte;
                JOptionPane.showMessageDialog(this,"Right-padded " + (8-bits) + " zero(es) to original data.","Pad successful",JOptionPane.INFORMATION_MESSAGE);
            }
        }
        if (Objects.equals(outputArea.getText(), OUTPUT_PLACEHOLDER)) {outputArea.setText("");}
        outputArea.append(String.format("Selected: %s | Lookup: %s\n", selectedCrc, useLookup ? "ON" : "OFF"));
        long start = System.nanoTime();
        if (mode == 1) {
            String lastCodeword = useLookup ? encodeLookup(data, poly, polyLength) : encodeBitwise(data, poly, polyLength);
            String remainder = lastCodeword.length() >= data.length() ? lastCodeword.substring(data.length()) : "";
            long end = System.nanoTime();
            outputArea.append("Data: " + data + "\n");
            outputArea.append("Polynomial: " + poly + "\n");
            outputArea.append("Remainder: " + (remainder.isEmpty() ? "N/A" : remainder) + "\n");
            outputArea.append("Codeword: " + lastCodeword + "\n");
            outputArea.append(String.format("Encode done in %.3f ms\n\n", (end - start) / 1e6));
            inputArea.setText(lastCodeword);
        } else if (mode == 2) {
            boolean valid = useLookup ? decodeLookup(data, poly, polyLength) : decodeBitwise(data, poly, polyLength);
            long end = System.nanoTime();
            outputArea.append("Codeword: " + data + "\n");
            outputArea.append(valid ? "✅ No error.\n" : "❌ Error detected.\n");
            outputArea.append(String.format("Decode done in %.3f ms\n\n", (end - start) / 1e6));
        }
    }

    // --- GUI & Utility ---
    private void simulateError() {
        String data = removeWhitespace(inputArea.getText());
        if (data.isEmpty() || !data.matches("[01]+")) {
            showError("Input must be binary.");
            return;
        }
        String input = JOptionPane.showInputDialog(this, "Bits to flip:", "1");
        if (input == null) return;
        int num;
        try {
            num = Integer.parseInt(input);
        } catch (NumberFormatException ex) {
            showError("Invalid number.");
            return;
        }
        if (num <= 0 || num > data.length()) {
            showError("Number of bits must be between 1 and " + data.length());
            return;
        }
        char[] bits = data.toCharArray();
        Random rand = new Random();
        Set<Integer> flipped = new HashSet<>();
        while (flipped.size() < num) {
            int pos = rand.nextInt(bits.length);
            if (flipped.add(pos)) bits[pos] = bits[pos] == '0' ? '1' : '0';
        }
        String corrupted = new String(bits);
        inputArea.setText(corrupted);
        JOptionPane.showMessageDialog(this, "Flipped " + num + " bit(s) at: " + flipped);
    }

    private void toggleAsciiMode() {
        asciiMode = !asciiMode;
        inputModeBtn.setText(asciiMode ? "Input mode: ASCII" : "Input mode: Binary");
    }

    private JPanel createLightPanel(String label) {
        JPanel container = new JPanel();
        JPanel light = new JPanel(new BorderLayout());
        light.setPreferredSize(new Dimension(20, 20));
        light.setBorder(new LineBorder(Color.DARK_GRAY));
        light.setBackground(Color.LIGHT_GRAY);
        JLabel mark = new JLabel("-", SwingConstants.CENTER);
        light.add(mark, BorderLayout.CENTER);
        light.putClientProperty("mark", mark);
        container.add(light);
        container.add(new JLabel(label));
        return container;
    }

    private void setLight(JPanel panel, Color color) {
        JPanel light = (JPanel) panel.getComponent(0);
        light.setBackground(color);
        JLabel mark = (JLabel) light.getClientProperty("mark");
        mark.setText(color == Color.GREEN ? "V" : color == Color.RED ? "X" : "-");
    }

    private void updateLights(){
        String poly = removeWhitespace(polyField.getText());
        setLight(notDivByXLight, Color.LIGHT_GRAY);
        setLight(divByXPlus1Light, Color.LIGHT_GRAY);
        if (poly.isEmpty()) {
            return;
        }
        String error = validatePoly(poly);
        if (!error.isEmpty()) {
            showError(error);
            polyField.requestFocus();
            polyField.selectAll();
            return;
        }
        boolean notDivByX = checkNotDivByX(poly);
        boolean divByXPlus1 = checkDivByXPlus1(poly);
        setLight(notDivByXLight, notDivByX ? Color.GREEN : Color.RED);
        setLight(divByXPlus1Light, divByXPlus1 ? Color.GREEN : Color.RED);

    }

    private String removeWhitespace(String s) {
        return s.replaceAll("\\s+", "");
    }

    private String validatePoly(String p) {
        if (!p.matches("[01]+")) {
            return "Polynomial must contain only 0 and 1.";
        }
        if (p.length() < 2) {
            return "Polynomial must be degree 1 or higher.";
        }
        if (p.charAt(0) != '1') {
            return "Polynomial must start with 1.";
        }
        return "";
    }

    private boolean checkNotDivByX(String poly) {
        return poly.charAt(poly.length() - 1) == '1';
    }

    private boolean checkDivByXPlus1(String poly) {
        int ones = 0;
        for (char c : poly.toCharArray()) if (c == '1') ones++;
        return ones % 2 == 0;
    }

    private String asciiToBinary(String text) {
        StringBuilder sb = new StringBuilder();
        for (char c : text.toCharArray()) {
            if (c > 255) throw new IllegalArgumentException("Non-ASCII character: " + c);
            sb.append(String.format("%8s", Integer.toBinaryString(c)).replace(' ', '0'));
        }
        return sb.toString();
    }

    private JTextArea addPlaceholder(JTextArea area, String placeholder) {
        area.setForeground(Color.GRAY);
        area.setText(placeholder);
        area.addFocusListener(new FocusAdapter() {
            @Override
            public void focusGained(FocusEvent e) {
                if (area.getText().equals(placeholder)) {
                    area.setText("");
                    area.setForeground(Color.BLACK);
                }
            }

            @Override
            public void focusLost(FocusEvent e) {
                if (area.getText().isEmpty()) {
                    area.setForeground(Color.GRAY);
                    area.setText(placeholder);
                }
            }
        });
        return area;
    }

    private void showError(String msg) {
        JOptionPane.showMessageDialog(this, msg, "Error", JOptionPane.ERROR_MESSAGE);
    }

    public static void main(String[] args) {
        SwingUtilities.invokeLater(CrcGui::new);
    }
}