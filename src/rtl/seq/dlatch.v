(* top *) module ff(
  (* iopad_external_pin *) output reg led,
  (* iopad_external_pin *) output led_oe,
  (* iopad_external_pin *) output clk_oe,
  (* iopad_external_pin *) input a,
  (* iopad_external_pin *) input clk,
  (* iopad_external_pin *) input rst 
);
  
  assign led_oe = 1'b1; assign clk_oe=1'b1;
  always @(*) begin
  if(clk)  led=a;
  end
endmodule
