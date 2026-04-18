A = [850 2 10 5 7;
     900 2 8 4 8;
     1200 3 5 3 9;
     1500 3 2 2 10];

B = [45; 50; 75; 95];

X = A \ B;

disp("Solution using Matrix Method:");
disp(X);