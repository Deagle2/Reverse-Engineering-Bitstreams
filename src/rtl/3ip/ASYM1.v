(* top *) module gate(
  (* iopad_external_pin *) output led,
  (* iopad_external_pin *) output led_oe,
  (* iopad_external_pin *) input a,
  (* iopad_external_pin *) input b,
  (* iopad_external_pin *) input c
);
  assign led_oe = 1'b1;
  assign led = a & ~b & c;
endmodule
