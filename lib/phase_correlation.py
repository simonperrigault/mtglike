import numpy as np
import matplotlib.pyplot as plt 
import time
from tqdm import trange

def tile_grid(im_now,im_past,tile_size,jump=0):

    if jump==0:
        jump = tile_size
    Nx,Ny = im_now.shape
    PosX = np.arange(0,Nx-tile_size,jump)
    PosY = np.arange(0,Ny-tile_size,jump)

    #we don't get into account the last row nd the last column of tiles bc they have different dimensions than the other, and will be entirely black anyway (for tile_size mall enough)

    L_tile_now  = np.array([[ im_now[i:i+tile_size,j:j+tile_size] for j in PosY] for i in PosX])
    L_tile_past = np.array([[im_past[i:i+tile_size,j:j+tile_size] for j in PosY] for i in PosX])

    center_tile = np.array([[[i+tile_size/2, j+tile_size/2] for j in PosY] for i in PosX])

    return L_tile_now, L_tile_past, center_tile

def fourier_flow(im_now,im_past,tile_size,jump,mode="max"):

    t0 = time.time()

    L_tile_now, L_tile_past, center_tile = tile_grid(im_now,im_past,tile_size,jump)

    move_tile = np.zeros(shape=L_tile_now.shape)

    Lx, Ly = len(L_tile_now), len(L_tile_now[0])

    flow = np.zeros((2,Lx,Ly))
    flow_mean = np.zeros((2,Lx,Ly))

    A = np.arange(0,tile_size,1)
    XX,YY = np.meshgrid(A,A)

    if mode=="max":

        for i in trange(Lx):
            for j in range(Ly):
                tile_now  =  L_tile_now[i,j]
                tile_past = L_tile_past[i,j]

                Ftile_now  =  np.fft.fft2(tile_now)
                Ftile_past = np.fft.fft2(tile_past)

                P = Ftile_past*np.conjugate(Ftile_now)
                R = np.where(np.absolute(P)!=0,P/np.absolute(P),0)
                move_tile[i,j] = np.fft.ifft2(R)

                V_max = np.unravel_index(np.argmax(move_tile[i,j]), move_tile[i,j].shape)

                if V_max[0]<=(tile_size-V_max[0]):
                    flow[0,i,j] = V_max[0]
                else:
                    flow[0,i,j] = V_max[0]-tile_size 

                if V_max[1]<=(tile_size-V_max[1]):
                    flow[1,i,j] = V_max[1]
                else:
                    flow[1,i,j] = V_max[1]-tile_size

        print("flow calculé en", time.time()-t0, "s")

        return flow, center_tile

    if mode=="both":

        for i in trange(Lx):
            for j in range(Ly):
                tile_now  =  L_tile_now[i,j]
                tile_past = L_tile_past[i,j]

                Ftile_now  =  np.fft.fft2(tile_now)
                Ftile_past = np.fft.fft2(tile_past)

                P = Ftile_past*np.conjugate(Ftile_now)
                R = np.where(np.absolute(P)!=0,P/np.absolute(P),0)
                move_tile[i,j] = np.fft.ifft2(R)

                V_max = np.unravel_index(np.argmax(move_tile[i,j]), move_tile[i,j].shape)

                if V_max[0]<=(tile_size-V_max[0]):
                    flow[0,i,j] = V_max[0]
                else:
                    flow[0,i,j] = V_max[0]-tile_size 

                if V_max[1]<=(tile_size-V_max[1]):
                    flow[1,i,j] = V_max[1]
                else:
                    flow[1,i,j] = V_max[1]-tile_size



                if np.sum(move_tile)==0:
                    V_mean = 0
                    flow_mean[i,j]=0

                else:
                    
                    V_mean = np.array([np.sum(XX*move_tile[i,j]),np.sum(YY*move_tile[i,j])])/np.sum(move_tile[i,j])

                    if V_mean[0]<=(tile_size-V_mean[0]):
                        flow_mean[0,i,j] = V_mean[0]
                    else:
                        flow_mean[0,i,j] = V_mean[0] - tile_size

                    if V_mean[1]<=(tile_size-V_mean[1]):
                        flow_mean[1,i,j] = V_mean[1]
                    else:
                        flow_mean[1,i,j] = V_mean[1]-tile_size

        print("flow calculé en", time.time()-t0, "s")

        return flow, flow_mean, center_tile


def display_flow(im_now,im_past,tile_size,jump=0,proportion=1, view="max"):

    flow, center_tile = fourier_flow(im_now,im_past,tile_size,jump)

    N = int(1/proportion)

    X = center_tile[::N, ::N, 0]
    Y = center_tile[::N, ::N, 1]

    U = flow[0,::N,::N]
    V = flow[1,::N,::N]

    # U_mean = flow_mean[0, ::N, ::N]
    # V_mean = flow_mean[1, ::N, ::N]


    if view=="max":

        fig = plt.figure()
        plt.imshow(im_now, cmap="gray")
        plt.quiver(X,Y,U,V,color="red",
                    angles="xy",
                    scale_units="xy",
                    scale=1)
        plt.show()
    
    # elif view=="mean":

    #     fig = plt.figure()
    #     plt.imshow(im_now)
    #     plt.quiver(X,Y,U_mean,V_mean,color="red")
    #     plt.show()

    # elif view == "dual":

    #     fig, axes = plt.subplots(1,2)
    #     axes[0].imshow(im_now)
    #     axes[0].quiver(X,Y,U,V,color="red")
        
    #     axes[1].imshow(im_now)
    #     axes[1].quiver(X,Y,U_mean,V_mean,color="red")

    #     plt.show()

    # elif view == "comparison":

    #     fig, axes = plt.subplots(1,3)

    #     axes[0].imshow(im_now)
    #     axes[0].quiver(X,Y,U,V,color="red")

    #     axes[1].imshow( np.power(U-U_mean,2)+np.power(V-V_mean,2) )
        
    #     axes[2].imshow(im_now)
    #     axes[2].quiver(X,Y,U_mean,V_mean,color="red")

    #     plt.show()

