(* top *) module gate(
  (* iopad_external_pin *) output led,
  (* iopad_external_pin *) output led_oe,
  (* iopad_external_pin *) input a,
  (* iopad_external_pin *) input b
);
  
  assign led_oe = 1'b1;
  assign led = ~a & b; // ANDNOT_BA
endmodule
